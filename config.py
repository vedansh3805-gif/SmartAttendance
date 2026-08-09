import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ── Flask ──────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-attend-2026-xK9pL2mN-change-in-prod'
    DEBUG = True

    # ── Database ───────────────────────────────────────
    DATABASE = os.path.join(BASE_DIR, 'attendance.db')

    # ── File Paths ─────────────────────────────────────
    UPLOAD_FOLDER  = os.path.join(BASE_DIR, 'static', 'uploads')
    DATASET_FOLDER = os.path.join(BASE_DIR, 'dataset')
    MODEL_FOLDER   = os.path.join(BASE_DIR, 'models')

    # ── Session ────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'

    # ── Uploads ────────────────────────────────────────
    MAX_CONTENT_LENGTH  = 16 * 1024 * 1024   # 16 MB
    ALLOWED_EXTENSIONS  = {'png', 'jpg', 'jpeg'}

    # ── Face Recognition ───────────────────────────────
    FACE_TOLERANCE        = 0.50          # lower = stricter
    FACE_IMAGES_REQUIRED  = 20
    FACE_DETECTION_MODEL  = 'hog'         # 'hog' (CPU) | 'cnn' (GPU)
    MIN_CONFIDENCE        = 60.0          # % to auto-mark attendance

    # ── Attendance ─────────────────────────────────────
    MIN_ATTENDANCE_PCT    = 75

    # ── App Data ───────────────────────────────────────
    DEPARTMENTS = [
        'CSE', 'ECE', 'EEE', 'MECH', 'CIVIL',
        'IT', 'AIDS', 'AIML', 'MBA', 'MCA'
    ]
    YEARS    = ['1st Year', '2nd Year', '3rd Year', '4th Year']
    SECTIONS = ['A', 'B', 'C', 'D', 'E']
    SUBJECTS = [
        'Mathematics I', 'Mathematics II', 'Physics', 'Chemistry', 'English',
        'Engineering Graphics', 'Data Structures', 'Algorithms',
        'Computer Science Fundamentals', 'Machine Learning', 'Deep Learning',
        'Web Development', 'Database Management Systems', 'Operating Systems',
        'Computer Networks', 'Software Engineering', 'Artificial Intelligence',
        'Python Programming', 'Cloud Computing', 'Cyber Security'
    ]

    @staticmethod
    def init_app(app):
        for folder in [Config.UPLOAD_FOLDER, Config.DATASET_FOLDER, Config.MODEL_FOLDER]:
            os.makedirs(folder, exist_ok=True)
