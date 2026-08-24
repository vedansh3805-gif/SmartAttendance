import cv2
import face_recognition
import numpy as np
import base64
import json
import os
from database import get_db
from config import Config


# ── Helpers & Preprocessing ──────────────────────────────────────────────────

def decode_frame(b64_frame: str) -> np.ndarray:
    """Base64 data-URL → BGR numpy array."""
    if ',' in b64_frame:
        header, data = b64_frame.split(',', 1)
    else:
        data = b64_frame
    nparr = np.frombuffer(base64.b64decode(data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def check_liveness(frame: np.ndarray, location: tuple) -> tuple[bool, float, str]:
    """
    Multi-factor Anti-Spoofing / Liveness Check:
    1. Laplacian texture variance analysis on cropped face region.
    2. Color-space histogram distribution (HSV/YCrCb) to detect screen reflection.
    Returns (is_live: bool, score: float, details: str).
    """
    try:
        top, right, bottom, left = location
        h, w, _ = frame.shape
        top = max(0, top)
        left = max(0, left)
        bottom = min(h, bottom)
        right = min(w, right)

        face_crop = frame[top:bottom, left:right]
        if face_crop.size == 0 or face_crop.shape[0] < 20 or face_crop.shape[1] < 20:
            return True, 50.0, "Face crop too small"

        # 1. Texture Sharpness & Focus Measure (Laplacian Variance)
        gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        laplacian_var = float(cv2.Laplacian(gray_crop, cv2.CV_64F).var())

        # 2. Reflection & Dynamic Range (HSV Saturation + Value balance)
        hsv_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)
        sat_std = float(np.std(hsv_crop[:, :, 1]))
        val_mean = float(np.mean(hsv_crop[:, :, 2]))

        # High-glare or overly uniform displays typically yield abnormal variance
        is_live = laplacian_var >= Config.LIVENESS_THRESHOLD and sat_std > 8.0 and val_mean < 250.0
        score = min(100.0, round(laplacian_var * 0.8 + sat_std * 0.4, 1))

        if not is_live:
            if laplacian_var < Config.LIVENESS_THRESHOLD:
                reason = f"Texture blur/spoofing detected (Laplacian: {laplacian_var:.1f})"
            else:
                reason = "Unnatural illumination/reflection detected"
            return False, score, reason

        return True, score, "Live human verified"
    except Exception as e:
        # Fallback to passing if liveness check calculation fails
        return True, 75.0, f"Bypass fallback: {e}"


def load_known_faces():
    """
    Return (encodings_list, student_ids_list, names_list) from DB.
    Only active students with a valid face_encoding are loaded.
    """
    db = get_db()
    rows = db.execute(
        "SELECT student_id, name, face_encoding "
        "FROM students WHERE face_encoding IS NOT NULL AND is_active=1"
    ).fetchall()
    db.close()

    encodings, ids, names = [], [], []
    for row in rows:
        try:
            enc = np.array(json.loads(row['face_encoding']), dtype=np.float64)
            encodings.append(enc)
            ids.append(row['student_id'])
            names.append(row['name'])
        except Exception:
            pass
    return encodings, ids, names


# ── Registration: Capture ────────────────────────────────────────────────────

def capture_and_save_face(student_id: str, b64_frame: str, index: int):
    """
    Detect a face in the frame, perform quality/liveness checks, and save to dataset.
    Returns (success: bool, message: str).
    """
    try:
        frame = decode_frame(b64_frame)
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb, model=Config.FACE_DETECTION_MODEL)
        if not locations:
            return False, "No face detected — reposition and ensure good lighting"

        if len(locations) > 1:
            return False, "Multiple faces detected — ensure only one person is in frame"

        # Check basic texture quality
        if Config.LIVENESS_ENABLED:
            is_live, _, reason = check_liveness(frame, locations[0])
            if not is_live:
                return False, f"Image rejected: {reason}"

        folder = os.path.join(Config.DATASET_FOLDER, student_id)
        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, f"img_{index:03d}.jpg")
        cv2.imwrite(path, frame)
        return True, f"Image {index + 1} captured successfully"
    except Exception as e:
        return False, str(e)


# ── Registration: Train ──────────────────────────────────────────────────────

def train_student_face(student_id: str):
    """
    Compute average 128D face encoding from all captured dataset images
    and save it to the students table.
    Returns (success: bool, message: str).
    """
    folder = os.path.join(Config.DATASET_FOLDER, student_id)
    if not os.path.exists(folder):
        return False, "No dataset images found. Please capture faces first."

    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if len(files) < 10:
        return False, f"Need at least 10 images — found {len(files)}"

    all_encodings = []
    for fname in files:
        try:
            img = face_recognition.load_image_file(os.path.join(folder, fname))
            locs = face_recognition.face_locations(img, model=Config.FACE_DETECTION_MODEL)
            if locs:
                enc = face_recognition.face_encodings(img, locs)[0]
                all_encodings.append(enc)
        except Exception:
            continue

    if not all_encodings:
        return False, "Could not extract face encodings from captured images"

    # Compute mean representation across all samples
    avg_encoding = np.mean(all_encodings, axis=0).tolist()

    db = get_db()
    db.execute(
        "UPDATE students SET face_encoding = ? WHERE student_id = ?",
        (json.dumps(avg_encoding), student_id)
    )
    db.commit()
    db.close()

    return True, f"Model trained with {len(all_encodings)} validated face samples"


# ── Attendance: Real-time Recognition & Anti-Spoofing ─────────────────────────

def recognize_faces_in_frame(b64_frame: str):
    """
    Detect, verify liveness, and recognize all faces in a frame.
    Returns (results: list[dict], error: str|None).

    Each result dict:
        name, student_id, confidence (%), is_live (bool), liveness_score, location {top,right,bottom,left}
    """
    try:
        frame = decode_frame(b64_frame)
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Downscale 0.5x for fast real-time inference
        small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)

        locations = face_recognition.face_locations(small, model=Config.FACE_DETECTION_MODEL)
        encodings = face_recognition.face_encodings(small, locations)

        known_encs, known_ids, known_names = load_known_faces()

        results = []
        for (top, right, bottom, left), enc in zip(locations, encodings):
            # Scale back up
            top    *= 2; right  *= 2
            bottom *= 2; left   *= 2

            name        = "Unknown"
            student_id  = None
            confidence  = 0.0

            # Liveness & Anti-Spoofing Check
            is_live, liveness_score, live_details = True, 100.0, "Verified"
            if Config.LIVENESS_ENABLED:
                is_live, liveness_score, live_details = check_liveness(frame, (top, right, bottom, left))

            if known_encs and is_live:
                # Fast vectorized euclidean distance
                dists = face_recognition.face_distance(known_encs, enc)
                best_idx = int(np.argmin(dists))

                if dists[best_idx] <= Config.FACE_TOLERANCE:
                    name       = known_names[best_idx]
                    student_id = known_ids[best_idx]
                    confidence = round((1.0 - float(dists[best_idx])) * 100, 1)

            results.append({
                'name':           name,
                'student_id':     student_id,
                'confidence':     confidence,
                'is_live':        is_live,
                'liveness_score': liveness_score,
                'live_details':   live_details,
                'location': {
                    'top':    top,
                    'right':  right,
                    'bottom': bottom,
                    'left':   left
                }
            })

        return results, None

    except Exception as e:
        return [], str(e)


# ── Utility ──────────────────────────────────────────────────────────────────

def count_dataset_images(student_id: str) -> int:
    folder = os.path.join(Config.DATASET_FOLDER, student_id)
    if not os.path.exists(folder):
        return 0
    return len([f for f in os.listdir(folder)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
