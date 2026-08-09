import cv2
import face_recognition
import numpy as np
import base64
import json
import os
from database import get_db
from config import Config


# ── Helpers ──────────────────────────────────────────────────────────────────

def decode_frame(b64_frame: str) -> np.ndarray:
    """Base64 data-URL → BGR numpy array."""
    header, data = b64_frame.split(',', 1)
    nparr = np.frombuffer(base64.b64decode(data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def load_known_faces():
    """
    Return (encodings_list, student_ids_list, names_list) from DB.
    Only students with a face_encoding AND is_active=1 are loaded.
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
            enc = np.array(json.loads(row['face_encoding']))
            encodings.append(enc)
            ids.append(row['student_id'])
            names.append(row['name'])
        except Exception:
            pass
    return encodings, ids, names


# ── Registration: Capture ────────────────────────────────────────────────────

def capture_and_save_face(student_id: str, b64_frame: str, index: int):
    """
    Detect a face in the frame and save the image to the dataset folder.
    Returns (success: bool, message: str).
    """
    try:
        frame = decode_frame(b64_frame)
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb, model='hog')
        if not locations:
            return False, "No face detected — reposition and try again"

        folder = os.path.join(Config.DATASET_FOLDER, student_id)
        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, f"img_{index:03d}.jpg")
        cv2.imwrite(path, frame)
        return True, f"Image {index + 1} saved"
    except Exception as e:
        return False, str(e)


# ── Registration: Train ──────────────────────────────────────────────────────

def train_student_face(student_id: str):
    """
    Compute average face encoding from all captured dataset images
    and save it to the students table.
    Returns (success: bool, message: str).
    """
    folder = os.path.join(Config.DATASET_FOLDER, student_id)
    if not os.path.exists(folder):
        return False, "No dataset images found. Please capture face first."

    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if len(files) < 10:
        return False, f"Need at least 10 images — found {len(files)}"

    all_encodings = []
    for fname in files:
        try:
            img  = face_recognition.load_image_file(os.path.join(folder, fname))
            locs = face_recognition.face_locations(img, model='hog')
            if locs:
                enc = face_recognition.face_encodings(img, locs)[0]
                all_encodings.append(enc)
        except Exception:
            continue

    if not all_encodings:
        return False, "Could not extract face encodings from images"

    avg = np.mean(all_encodings, axis=0).tolist()

    db = get_db()
    db.execute(
        "UPDATE students SET face_encoding = ? WHERE student_id = ?",
        (json.dumps(avg), student_id)
    )
    db.commit()
    db.close()

    return True, f"Training complete — {len(all_encodings)} images used"


# ── Attendance: Recognize ────────────────────────────────────────────────────

def recognize_faces_in_frame(b64_frame: str):
    """
    Detect and recognise all faces in a base64-encoded frame.
    Returns (results: list[dict], error: str|None).

    Each result dict:
        name, student_id, confidence (%), location {top,right,bottom,left}
    """
    try:
        frame = decode_frame(b64_frame)
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Downscale for speed; we scale coords back afterwards
        small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)

        locations  = face_recognition.face_locations(small, model='hog')
        encodings  = face_recognition.face_encodings(small, locations)

        known_encs, known_ids, known_names = load_known_faces()

        results = []
        for (top, right, bottom, left), enc in zip(locations, encodings):
            top    *= 2; right  *= 2
            bottom *= 2; left   *= 2

            name        = "Unknown"
            student_id  = None
            confidence  = 0.0

            if known_encs:
                dists    = face_recognition.face_distance(known_encs, enc)
                best_idx = int(np.argmin(dists))

                if dists[best_idx] <= Config.FACE_TOLERANCE:
                    name       = known_names[best_idx]
                    student_id = known_ids[best_idx]
                    confidence = round((1 - dists[best_idx]) * 100, 1)

            results.append({
                'name':       name,
                'student_id': student_id,
                'confidence': confidence,
                'location':   {
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
