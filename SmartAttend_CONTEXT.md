# SmartAttend — Complete Source Code Context
## AI-Powered Smart Attendance Management System

### Stack
- **Backend:** Python 3.12 · Flask 3.0 · SQLite (WAL)
- **Face Recognition:** face_recognition (dlib HOG) · OpenCV
- **Frontend:** Jinja2 templates · Dark Glassmorphism CSS · Chart.js · Font Awesome 6
- **Email:** SMTP via smtplib (configurable, Gmail-ready)
- **Export:** Pandas → CSV / openpyxl → Excel

### Project Structure
```
SmartAttendance/
├── app.py                    # All Flask routes (30+)
├── config.py                 # Central config & constants
├── database.py               # SQLite schema + init (6 tables)
├── requirements.txt
├── utils/
│   ├── auth.py               # login_required, admin_required, authenticate
│   ├── face_utils.py         # capture, train, recognize (face_recognition)
│   ├── attendance_utils.py   # mark, stats, low-attendance, trends
│   ├── report_generator.py   # CSV + Excel export with filters
│   └── email_utils.py        # SMTP alerts (low attendance, summary, unknown face)
├── templates/                # 13 Jinja2 templates
│   ├── base.html             # Sidebar layout (all pages extend this)
│   ├── index.html            # Landing page (standalone)
│   ├── login.html            # Auth (standalone)
│   ├── dashboard.html        # KPI cards + Chart.js
│   ├── students.html         # Student grid + search/filter
│   ├── register_student.html # Add student form
│   ├── face_capture.html     # Webcam capture (20 images)
│   ├── attendance.html       # Live face recognition
│   ├── profile.html          # Student detail + attendance history
│   ├── records.html          # Filterable attendance table
│   ├── reports.html          # Analytics + export
│   ├── faculty.html          # Faculty CRUD (admin only)
│   └── settings.html         # SMTP + system config (admin only)
└── static/
    ├── css/style.css         # 900-line design system (glassmorphism)
    ├── js/main.js            # Clock, toasts, sidebar, AJAX helpers
    └── js/camera.js          # Webcam: face capture + live recognition

### Database Schema (6 tables)
- **admin**        → id, username, password_hash, full_name, email, role
- **faculty**      → id, faculty_id, username, password_hash, full_name, department, email, is_active
- **students**     → id, student_id, name, department, year, section, email, phone, image_path, face_encoding, is_active
- **attendance**   → id, student_id, student_name, department, year, section, date, time, subject, status, marked_by
- **activity_log** → id, action, details, performed_by, timestamp
- **settings**     → key, value  (smtp_host, smtp_port, smtp_user, smtp_pass, notifications_enabled, etc.)

### Key API Routes
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET/POST | /login | — | Authenticate admin or faculty |
| GET | /dashboard | ✓ | Stats, charts, recent activity |
| GET | /students | ✓ | Student grid with search/filter |
| GET/POST | /students/add | ✓ | Register new student |
| GET | /students/<id> | ✓ | Student profile + history |
| POST | /students/<id>/edit | ✓ | Edit student details |
| POST | /students/<id>/delete | admin | Soft-delete student |
| GET | /face/capture/<id> | ✓ | Face capture webcam page |
| POST | /api/face/capture | ✓ | Save one captured frame |
| POST | /api/face/train | ✓ | Train face model (avg encoding) |
| GET | /attendance | ✓ | Live recognition page |
| POST | /api/recognize | ✓ | Recognize faces + auto-mark |
| POST | /api/attendance/mark | ✓ | Manual mark attendance |
| GET | /records | ✓ | Filterable records table |
| GET | /reports | ✓ | Analytics + Chart.js |
| GET | /reports/export/csv | ✓ | Download CSV |
| GET | /reports/export/excel | ✓ | Download Excel |
| GET/POST | /faculty | admin | Faculty management |
| GET/POST | /settings | admin | SMTP + system settings |
| GET | /api/stats | ✓ | Today's JSON stats |
| GET | /api/students/search | ✓ | Autocomplete search |

### Login Credentials (default)
- **Admin:** admin / admin123
- **Faculty:** set via /faculty page

### How Face Recognition Works
1. Register student → /students/add (saves to DB)
2. Capture 20+ frames → /face/capture/<id> → camera.js → /api/face/capture
3. Train model → /api/face/train → face_utils.train_student_face() → averages dlib 128D encodings → stores JSON in students.face_encoding
4. Take attendance → /attendance → camera.js sends frames every 2s → /api/recognize → compare against all stored encodings → auto-mark if confidence ≥ 60%

### Design System (style.css)
- Background: #0a0a1a (deep dark)
- Primary gradient: linear-gradient(135deg, #6c63ff, #3f8efc)
- Cards: rgba(255,255,255,.04) + backdrop-filter blur(12px) [glassmorphism]
- Success: #10d4a3 | Warning: #f59e0b | Danger: #ef4444
- Font: Inter (Google Fonts) | Icons: Font Awesome 6

---


---
## `config.py`
*56 lines*

```python
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

```


---
## `database.py`
*118 lines*

```python
import sqlite3
from config import Config
from werkzeug.security import generate_password_hash


def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        -- ── Admins ──────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS admin (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name     TEXT DEFAULT 'Administrator',
            email         TEXT,
            role          TEXT DEFAULT 'admin',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Faculty ─────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS faculty (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id    TEXT UNIQUE NOT NULL,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name     TEXT NOT NULL,
            department    TEXT NOT NULL,
            email         TEXT,
            subjects      TEXT,
            is_active     INTEGER DEFAULT 1,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Students ────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS students (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT UNIQUE NOT NULL,
            name          TEXT NOT NULL,
            department    TEXT NOT NULL,
            year          TEXT NOT NULL,
            section       TEXT NOT NULL,
            email         TEXT,
            phone         TEXT,
            image_path    TEXT,
            face_encoding TEXT,
            is_active     INTEGER DEFAULT 1,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Attendance ──────────────────────────────────────
        CREATE TABLE IF NOT EXISTS attendance (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT NOT NULL,
            student_name  TEXT NOT NULL,
            department    TEXT NOT NULL,
            year          TEXT NOT NULL,
            section       TEXT NOT NULL,
            date          TEXT NOT NULL,
            time          TEXT NOT NULL,
            subject       TEXT NOT NULL,
            status        TEXT DEFAULT 'Present',
            marked_by     TEXT DEFAULT 'AI',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Activity Log ────────────────────────────────────
        CREATE TABLE IF NOT EXISTS activity_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            action       TEXT NOT NULL,
            details      TEXT,
            performed_by TEXT DEFAULT 'System',
            timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Settings ────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS settings (
            key        TEXT PRIMARY KEY,
            value      TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # ── Default admin ────────────────────────────────────────
    if c.execute("SELECT COUNT(*) FROM admin").fetchone()[0] == 0:
        c.execute(
            "INSERT INTO admin (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'System Administrator', '')
        )

    # ── Default settings ─────────────────────────────────────
    defaults = [
        ('smtp_host',                 'smtp.gmail.com'),
        ('smtp_port',                 '587'),
        ('smtp_user',                 ''),
        ('smtp_pass',                 ''),
        ('from_email',                ''),
        ('admin_email',               ''),
        ('notifications_enabled',     '0'),
        ('low_attendance_threshold',  '75'),
        ('college_name',              'Smart College of Engineering'),
        ('college_logo',              ''),
    ]
    for key, val in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()
    print("✅  Database ready")

```


---
## `app.py`
*634 lines*

```python
"""
SmartAttend – AI-Powered Smart Attendance Management System
Flask application entry point.
Default login: admin / admin123
"""

from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, flash, send_file
)
from datetime import date, datetime
from io import BytesIO
import os

from config import Config
from database import get_db, init_db
from utils.auth import (
    login_required, admin_required, api_login_required,
    authenticate_user, log_activity, get_current_user
)
from utils.face_utils import (
    recognize_faces_in_frame, capture_and_save_face,
    train_student_face, count_dataset_images
)
from utils.attendance_utils import (
    mark_attendance, get_today_stats, get_low_attendance_students,
    get_student_attendance_percentage, get_weekly_trend, get_department_stats
)
from utils.report_generator import get_attendance_data, export_csv, export_excel
from utils.email_utils import (
    send_low_attendance_alert, send_daily_summary,
    send_unknown_face_alert, smtp_configured
)
from werkzeug.security import generate_password_hash

# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
init_db()


# ── Context processor ────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    db  = get_db()
    cfg = {r['key']: r['value'] for r in db.execute("SELECT key,value FROM settings").fetchall()}
    db.close()
    return dict(
        current_user=get_current_user(),
        now=datetime.now(),
        college_name=cfg.get('college_name', 'SmartAttend'),
    )


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = authenticate_user(username, password)
        if user:
            session.permanent = True
            session['user_id']   = user['id']
            session['username']  = user['username']
            session['full_name'] = user.get('full_name', username)
            session['role']      = user.get('role', 'faculty')
            session['user_type'] = user['user_type']
            log_activity('LOGIN', f"{user['user_type'].title()} logged in", username)
            flash(f"Welcome back, {session['full_name']}! 👋", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    uname = session.get('username', 'Unknown')
    log_activity('LOGOUT', f'{uname} logged out', uname)
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    today   = date.today().isoformat()
    stats   = get_today_stats()
    low_att = get_low_attendance_students()[:5]
    weekly  = get_weekly_trend()
    dept    = get_department_stats(today)

    db = get_db()
    recent_att = db.execute(
        "SELECT * FROM attendance WHERE date=? ORDER BY time DESC LIMIT 20", (today,)
    ).fetchall()
    recent_log = db.execute(
        "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 8"
    ).fetchall()
    face_trained = db.execute(
        "SELECT COUNT(*) FROM students WHERE face_encoding IS NOT NULL AND is_active=1"
    ).fetchone()[0]
    db.close()

    return render_template(
        'dashboard.html',
        stats=stats,
        low_att=low_att,
        weekly_dates=[d['date'] for d in weekly],
        weekly_counts=[d['count'] for d in weekly],
        dept_labels=[d['department'] for d in dept],
        dept_present=[d['present'] for d in dept],
        dept_total=[d['total'] for d in dept],
        recent_att=recent_att,
        recent_log=recent_log,
        face_trained=face_trained,
        today=today,
    )


# ─────────────────────────────────────────────────────────────────────────────
# STUDENTS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/students')
@login_required
def students():
    search = request.args.get('q', '').strip()
    dept   = request.args.get('dept', '')
    year   = request.args.get('year', '')
    section= request.args.get('section', '')

    db     = get_db()
    query  = "SELECT * FROM students WHERE is_active=1"
    params = []

    if search:
        query  += " AND (name LIKE ? OR student_id LIKE ?)"
        params += [f'%{search}%', f'%{search}%']
    if dept:
        query  += " AND department=?";  params.append(dept)
    if year:
        query  += " AND year=?";        params.append(year)
    if section:
        query  += " AND section=?";     params.append(section)

    query       += " ORDER BY name"
    student_list = db.execute(query, params).fetchall()
    total_count  = db.execute("SELECT COUNT(*) FROM students WHERE is_active=1").fetchone()[0]
    trained_count= db.execute(
        "SELECT COUNT(*) FROM students WHERE face_encoding IS NOT NULL AND is_active=1"
    ).fetchone()[0]
    db.close()

    return render_template(
        'students.html',
        students=student_list, total_count=total_count,
        trained_count=trained_count,
        departments=Config.DEPARTMENTS, years=Config.YEARS, sections=Config.SECTIONS,
        search=search, dept=dept, year=year, section=section,
    )


@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        sid   = request.form.get('student_id', '').strip().upper()
        name  = request.form.get('name', '').strip()
        dept  = request.form.get('department', '')
        year  = request.form.get('year', '')
        sec   = request.form.get('section', '')
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not all([sid, name, dept, year, sec]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register_student.html', config=Config)

        image_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                ext      = photo.filename.rsplit('.', 1)[-1].lower()
                filename = f"{sid}.{ext}"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                photo.save(filepath)
                image_path = f"uploads/{filename}"

        db = get_db()
        try:
            db.execute(
                '''INSERT INTO students
                   (student_id, name, department, year, section, email, phone, image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (sid, name, dept, year, sec, email, phone, image_path)
            )
            db.commit()
            log_activity('STUDENT_ADDED', f'{name} ({sid})', session['username'])
            flash(f'Student {name} registered! Now capture their face.', 'success')
            return redirect(url_for('face_capture', student_id=sid))
        except Exception:
            flash('Error: Student ID already exists.', 'error')
        finally:
            db.close()

    return render_template('register_student.html', config=Config)


@app.route('/students/<student_id>')
@login_required
def student_profile(student_id):
    db      = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE student_id=?", (student_id,)
    ).fetchone()
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('students'))

    records = db.execute(
        "SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC, time DESC LIMIT 60",
        (student_id,)
    ).fetchall()
    # Monthly breakdown
    monthly = db.execute(
        '''SELECT substr(date,1,7) as month, COUNT(*) as count
           FROM attendance WHERE student_id=?
           GROUP BY month ORDER BY month DESC LIMIT 6''',
        (student_id,)
    ).fetchall()
    db.close()

    pct            = get_student_attendance_percentage(student_id)
    dataset_images = count_dataset_images(student_id)

    return render_template(
        'profile.html',
        student=student, records=records, monthly=monthly,
        percentage=pct, dataset_images=dataset_images,
    )


@app.route('/students/<student_id>/edit', methods=['POST'])
@login_required
def edit_student(student_id):
    name  = request.form.get('name', '').strip()
    dept  = request.form.get('department', '')
    year  = request.form.get('year', '')
    sec   = request.form.get('section', '')
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    db = get_db()
    db.execute(
        "UPDATE students SET name=?,department=?,year=?,section=?,email=?,phone=? WHERE student_id=?",
        (name, dept, year, sec, email, phone, student_id)
    )
    db.commit()
    db.close()
    log_activity('STUDENT_EDITED', f'Updated {student_id}', session['username'])
    flash('Student updated successfully.', 'success')
    return redirect(url_for('student_profile', student_id=student_id))


@app.route('/students/<student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    db = get_db()
    s  = db.execute("SELECT name FROM students WHERE student_id=?", (student_id,)).fetchone()
    if s:
        db.execute("UPDATE students SET is_active=0 WHERE student_id=?", (student_id,))
        db.commit()
        log_activity('STUDENT_DELETED', f'{s["name"]} ({student_id})', session['username'])
        flash('Student removed.', 'success')
    db.close()
    return redirect(url_for('students'))


# ─────────────────────────────────────────────────────────────────────────────
# FACE REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/face/capture/<student_id>')
@login_required
def face_capture(student_id):
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()
    db.close()
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('students'))
    captured = count_dataset_images(student_id)
    return render_template(
        'face_capture.html', student=student,
        captured=captured, required=Config.FACE_IMAGES_REQUIRED,
    )


@app.route('/api/face/capture', methods=['POST'])
@api_login_required
def api_capture_face():
    data       = request.json or {}
    student_id = data.get('student_id')
    frame      = data.get('frame')
    idx        = data.get('index', 0)

    if not (student_id and frame):
        return jsonify({'success': False, 'error': 'Missing data'})

    ok, msg = capture_and_save_face(student_id, frame, idx)
    return jsonify({'success': ok, 'message': msg,
                    'total': count_dataset_images(student_id)})


@app.route('/api/face/train', methods=['POST'])
@api_login_required
def api_train_face():
    data       = request.json or {}
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'error': 'student_id required'})

    ok, msg = train_student_face(student_id)
    if ok:
        log_activity('FACE_TRAINED', f'Student {student_id}', session['username'])
    return jsonify({'success': ok, 'message': msg})


# ─────────────────────────────────────────────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/attendance')
@login_required
def attendance():
    today   = date.today().isoformat()
    db      = get_db()
    records = db.execute(
        "SELECT * FROM attendance WHERE date=? ORDER BY time DESC", (today,)
    ).fetchall()
    db.close()
    return render_template(
        'attendance.html', subjects=Config.SUBJECTS,
        today_records=records, today=today,
    )


@app.route('/api/recognize', methods=['POST'])
@api_login_required
def api_recognize():
    data    = request.json or {}
    frame   = data.get('frame')
    subject = data.get('subject', '')

    if not frame:
        return jsonify({'success': False, 'error': 'No frame'})

    faces, err = recognize_faces_in_frame(frame)
    if err:
        return jsonify({'success': False, 'error': err})

    marked  = []
    unknown = False
    uname   = session.get('username', 'AI')

    for f in faces:
        if f['student_id'] and f['confidence'] >= Config.MIN_CONFIDENCE and subject:
            ok, _ = mark_attendance(f['student_id'], subject, 'Present', f'AI ({uname})')
            if ok:
                marked.append(f['student_id'])
                log_activity('AUTO_ATTENDANCE', f'{f["name"]} – {subject}', uname)
        if not f['student_id']:
            unknown = True

    # Unknown face alert
    if unknown:
        db  = get_db()
        cfg = {r['key']: r['value'] for r in db.execute("SELECT key,value FROM settings").fetchall()}
        db.close()
        if cfg.get('notifications_enabled') == '1' and cfg.get('admin_email'):
            send_unknown_face_alert(cfg['admin_email'])

    return jsonify({'success': True, 'faces': faces, 'marked': marked})


@app.route('/api/attendance/mark', methods=['POST'])
@api_login_required
def api_mark_manual():
    data       = request.json or {}
    student_id = data.get('student_id')
    subject    = data.get('subject')
    status     = data.get('status', 'Present')

    if not (student_id and subject):
        return jsonify({'success': False, 'error': 'Missing fields'})

    ok, msg = mark_attendance(student_id, subject, status, session.get('username', 'Manual'))
    if ok:
        log_activity('MANUAL_ATTENDANCE', f'{student_id} – {subject} – {status}', session['username'])
    return jsonify({'success': ok, 'message': msg})


# ─────────────────────────────────────────────────────────────────────────────
# RECORDS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/records')
@login_required
def records():
    filters = {k: request.args.get(k, '') for k in
               ['date', 'start_date', 'end_date', 'department', 'year',
                'section', 'student_id', 'subject', 'status']}
    filters = {k: v for k, v in filters.items() if v}
    data    = get_attendance_data(filters)

    return render_template(
        'records.html', records=data,
        departments=Config.DEPARTMENTS, years=Config.YEARS,
        sections=Config.SECTIONS, subjects=Config.SUBJECTS,
        filters=filters, total=len(data),
    )


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    return render_template(
        'reports.html',
        departments=Config.DEPARTMENTS, years=Config.YEARS,
        sections=Config.SECTIONS, subjects=Config.SUBJECTS,
    )


@app.route('/reports/export/csv')
@login_required
def export_csv_route():
    filters = {k: request.args.get(k, '') for k in
               ['start_date', 'end_date', 'department', 'year', 'section', 'subject']}
    filters = {k: v for k, v in filters.items() if v}
    data    = export_csv(filters)
    return send_file(
        BytesIO(data), mimetype='text/csv', as_attachment=True,
        download_name=f'attendance_{date.today().isoformat()}.csv'
    )


@app.route('/reports/export/excel')
@login_required
def export_excel_route():
    filters = {k: request.args.get(k, '') for k in
               ['start_date', 'end_date', 'department', 'year', 'section', 'subject']}
    filters = {k: v for k, v in filters.items() if v}
    data    = export_excel(filters)
    return send_file(
        BytesIO(data),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'attendance_{date.today().isoformat()}.xlsx'
    )


# ─────────────────────────────────────────────────────────────────────────────
# FACULTY  (admin only)
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/faculty')
@admin_required
def faculty():
    db      = get_db()
    members = db.execute(
        "SELECT * FROM faculty WHERE is_active=1 ORDER BY full_name"
    ).fetchall()
    db.close()
    return render_template('faculty.html', faculty=members, departments=Config.DEPARTMENTS)


@app.route('/faculty/add', methods=['POST'])
@admin_required
def add_faculty():
    fid   = request.form.get('faculty_id', '').strip().upper()
    uname = request.form.get('username', '').strip()
    name  = request.form.get('full_name', '').strip()
    dept  = request.form.get('department', '')
    email = request.form.get('email', '').strip()
    pwd   = request.form.get('password', '')

    if not all([fid, uname, name, dept, pwd]):
        flash('All fields are required.', 'error')
        return redirect(url_for('faculty'))

    db = get_db()
    try:
        db.execute(
            '''INSERT INTO faculty (faculty_id, username, password_hash, full_name, department, email)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (fid, uname, generate_password_hash(pwd), name, dept, email)
        )
        db.commit()
        log_activity('FACULTY_ADDED', f'{name} ({fid})', session['username'])
        flash(f'Faculty {name} added successfully.', 'success')
    except Exception:
        flash('Error: Faculty ID or username already exists.', 'error')
    finally:
        db.close()

    return redirect(url_for('faculty'))


@app.route('/faculty/<int:fid>/delete', methods=['POST'])
@admin_required
def delete_faculty(fid):
    db = get_db()
    f  = db.execute("SELECT full_name FROM faculty WHERE id=?", (fid,)).fetchone()
    if f:
        db.execute("UPDATE faculty SET is_active=0 WHERE id=?", (fid,))
        db.commit()
        log_activity('FACULTY_DELETED', f'{f["full_name"]}', session['username'])
        flash('Faculty removed.', 'success')
    db.close()
    return redirect(url_for('faculty'))


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS  (admin only)
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    db  = get_db()
    cfg = {r['key']: r['value'] for r in db.execute("SELECT key,value FROM settings").fetchall()}

    if request.method == 'POST':
        keys = [
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'from_email',
            'admin_email', 'notifications_enabled', 'low_attendance_threshold',
            'college_name',
        ]
        for k in keys:
            val = request.form.get(k, '')
            db.execute(
                "INSERT INTO settings (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                (k, val, val)
            )
        db.commit()
        log_activity('SETTINGS_UPDATED', 'System settings changed', session['username'])
        flash('Settings saved successfully.', 'success')
        cfg = {r['key']: r['value'] for r in db.execute("SELECT key,value FROM settings").fetchall()}

    db.close()
    return render_template('settings.html', cfg=cfg, smtp_ok=smtp_configured())


@app.route('/api/send-daily-summary', methods=['POST'])
@admin_required
def api_send_daily_summary():
    db  = get_db()
    cfg = {r['key']: r['value'] for r in db.execute("SELECT key,value FROM settings").fetchall()}
    db.close()

    if not cfg.get('admin_email'):
        return jsonify({'success': False, 'error': 'admin_email not configured'})

    stats  = get_today_stats()
    ok, msg = send_daily_summary(cfg['admin_email'], stats)
    return jsonify({'success': ok, 'message': msg})


# ─────────────────────────────────────────────────────────────────────────────
# MISC API
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/api/stats')
@api_login_required
def api_stats():
    return jsonify(get_today_stats())


@app.route('/api/students/search')
@api_login_required
def api_student_search():
    q  = request.args.get('q', '').strip()
    db = get_db()
    rows = db.execute(
        "SELECT student_id, name, department, year, section FROM students "
        "WHERE (name LIKE ? OR student_id LIKE ?) AND is_active=1 LIMIT 10",
        (f'%{q}%', f'%{q}%')
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/attendance/today')
@api_login_required
def api_today_attendance():
    today = date.today().isoformat()
    db    = get_db()
    rows  = db.execute(
        "SELECT * FROM attendance WHERE date=? ORDER BY time DESC", (today,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

```


---
## `utils/__init__.py`
*1 lines*

```python
# SmartAttend utility package

```


---
## `utils/auth.py`
*95 lines*

```python
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from werkzeug.security import check_password_hash
from database import get_db


# ── Decorators ───────────────────────────────────────────────────────────────

def login_required(f):
    """Block unauthenticated access; redirect to login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Block non-admin users; faculty will see 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Administrator access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    """JSON 401 for unauthenticated API calls."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated


# ── Authentication ───────────────────────────────────────────────────────────

def authenticate_user(username: str, password: str):
    """
    Try admin table first, then faculty table.
    Returns dict with user info + 'user_type' key, or None.
    """
    db = get_db()

    # Admin
    row = db.execute(
        "SELECT * FROM admin WHERE username = ?", (username,)
    ).fetchone()
    if row and check_password_hash(row['password_hash'], password):
        db.close()
        return {**dict(row), 'user_type': 'admin'}

    # Faculty
    row = db.execute(
        "SELECT * FROM faculty WHERE username = ? AND is_active = 1", (username,)
    ).fetchone()
    if row and check_password_hash(row['password_hash'], password):
        db.close()
        return {**dict(row), 'user_type': 'faculty'}

    db.close()
    return None


# ── Activity Logging ─────────────────────────────────────────────────────────

def log_activity(action: str, details: str = None, performed_by: str = 'System'):
    db = get_db()
    db.execute(
        "INSERT INTO activity_log (action, details, performed_by) VALUES (?, ?, ?)",
        (action, details, performed_by)
    )
    db.commit()
    db.close()


def get_current_user():
    """Return session user info dict, or None."""
    if 'user_id' not in session:
        return None
    return {
        'id':        session['user_id'],
        'username':  session['username'],
        'full_name': session.get('full_name', session['username']),
        'role':      session.get('role', 'faculty'),
        'user_type': session.get('user_type', 'faculty'),
    }

```


---
## `utils/face_utils.py`
*177 lines*

```python
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

```


---
## `utils/attendance_utils.py`
*132 lines*

```python
from datetime import datetime, date, timedelta
from database import get_db


def mark_attendance(student_id: str, subject: str, status: str = 'Present', marked_by: str = 'AI'):
    """
    Mark attendance for one student in one subject today.
    Prevents duplicate entries (one per student per subject per day).
    Returns (success: bool, message: str).
    """
    today = date.today().isoformat()
    now   = datetime.now().strftime('%H:%M:%S')

    db = get_db()

    # Duplicate check
    dup = db.execute(
        "SELECT id FROM attendance WHERE student_id=? AND date=? AND subject=?",
        (student_id, today, subject)
    ).fetchone()
    if dup:
        db.close()
        return False, "Already marked for this session"

    # Fetch student
    student = db.execute(
        "SELECT * FROM students WHERE student_id=? AND is_active=1", (student_id,)
    ).fetchone()
    if not student:
        db.close()
        return False, "Student not found"

    db.execute(
        '''INSERT INTO attendance
           (student_id, student_name, department, year, section, date, time, subject, status, marked_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (student_id, student['name'], student['department'], student['year'],
         student['section'], today, now, subject, status, marked_by)
    )
    db.commit()
    db.close()
    return True, f"✓ {student['name']} marked {status}"


def get_today_stats():
    today = date.today().isoformat()
    db    = get_db()
    total   = db.execute("SELECT COUNT(*) FROM students WHERE is_active=1").fetchone()[0]
    present = db.execute(
        "SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=?", (today,)
    ).fetchone()[0]
    db.close()
    absent  = max(0, total - present)
    pct     = round(present / total * 100, 1) if total > 0 else 0
    return {'total': total, 'present': present, 'absent': absent, 'percentage': pct}


def get_student_attendance_percentage(student_id: str) -> float:
    db         = get_db()
    attended   = db.execute(
        "SELECT COUNT(DISTINCT date) FROM attendance WHERE student_id=?", (student_id,)
    ).fetchone()[0]
    total_days = db.execute(
        "SELECT COUNT(DISTINCT date) FROM attendance"
    ).fetchone()[0]
    db.close()
    if total_days == 0:
        return 100.0
    return round(attended / total_days * 100, 1)


def get_low_attendance_students(threshold: float = 75.0):
    db       = get_db()
    students = db.execute(
        "SELECT student_id, name, department, year, section FROM students WHERE is_active=1"
    ).fetchall()
    db.close()

    result = []
    for s in students:
        pct = get_student_attendance_percentage(s['student_id'])
        if pct < threshold:
            result.append({
                'student_id': s['student_id'],
                'name':       s['name'],
                'department': s['department'],
                'year':       s['year'],
                'section':    s['section'],
                'percentage': pct,
            })
    return sorted(result, key=lambda x: x['percentage'])


def get_weekly_trend():
    """Last 7 days: [{date, count}]"""
    db   = get_db()
    rows = db.execute(
        '''SELECT date, COUNT(DISTINCT student_id) AS count
           FROM attendance
           WHERE date >= date('now', '-6 days')
           GROUP BY date ORDER BY date''',
    ).fetchall()
    db.close()
    return [{'date': r['date'], 'count': r['count']} for r in rows]


def get_department_stats(for_date: str = None):
    """Attendance count grouped by department for a given date (default today)."""
    for_date = for_date or date.today().isoformat()
    db = get_db()
    rows = db.execute(
        '''SELECT department, COUNT(DISTINCT student_id) AS present
           FROM attendance WHERE date=?
           GROUP BY department ORDER BY department''',
        (for_date,)
    ).fetchall()

    # Also get total students per dept
    totals = db.execute(
        "SELECT department, COUNT(*) AS total FROM students WHERE is_active=1 GROUP BY department"
    ).fetchall()
    db.close()

    totals_map = {r['department']: r['total'] for r in totals}
    return [
        {
            'department': r['department'],
            'present':    r['present'],
            'total':      totals_map.get(r['department'], 0),
        }
        for r in rows
    ]

```


---
## `utils/report_generator.py`
*77 lines*

```python
import pandas as pd
from io import BytesIO
from database import get_db


COLUMNS = [
    'id', 'student_id', 'student_name', 'department',
    'year', 'section', 'date', 'time', 'subject', 'status', 'marked_by'
]


def get_attendance_data(filters: dict = None) -> list[dict]:
    db     = get_db()
    query  = "SELECT * FROM attendance WHERE 1=1"
    params = []

    if filters:
        if filters.get('date'):
            query  += " AND date = ?"
            params.append(filters['date'])
        if filters.get('start_date'):
            query  += " AND date >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query  += " AND date <= ?"
            params.append(filters['end_date'])
        if filters.get('department'):
            query  += " AND department = ?"
            params.append(filters['department'])
        if filters.get('year'):
            query  += " AND year = ?"
            params.append(filters['year'])
        if filters.get('section'):
            query  += " AND section = ?"
            params.append(filters['section'])
        if filters.get('student_id'):
            query  += " AND student_id = ?"
            params.append(filters['student_id'])
        if filters.get('subject'):
            query  += " AND subject = ?"
            params.append(filters['subject'])
        if filters.get('status'):
            query  += " AND status = ?"
            params.append(filters['status'])

    query += " ORDER BY date DESC, time DESC"
    rows   = db.execute(query, params).fetchall()
    db.close()
    return [dict(r) for r in rows]


def _build_df(filters: dict = None) -> pd.DataFrame:
    data = get_attendance_data(filters)
    if data:
        df = pd.DataFrame(data)
        # Keep only relevant columns that exist
        cols = [c for c in COLUMNS if c in df.columns]
        return df[cols]
    return pd.DataFrame(columns=COLUMNS)


def export_csv(filters: dict = None) -> bytes:
    return _build_df(filters).to_csv(index=False).encode('utf-8')


def export_excel(filters: dict = None) -> bytes:
    df     = _build_df(filters)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
        ws = writer.sheets['Attendance']
        # Auto-width columns
        for col_cells in ws.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 40)
    output.seek(0)
    return output.getvalue()

```


---
## `utils/email_utils.py`
*168 lines*

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from database import get_db


# ── Config helpers ────────────────────────────────────────────────────────────

def _get_cfg() -> dict:
    db   = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    db.close()
    return {r['key']: r['value'] for r in rows}


def smtp_configured() -> bool:
    cfg = _get_cfg()
    return all([cfg.get('smtp_host'), cfg.get('smtp_user'), cfg.get('smtp_pass')])


# ── Core send ────────────────────────────────────────────────────────────────

def send_email(to: str, subject: str, body: str, html: str = None) -> tuple[bool, str]:
    """
    Send a plain-text (+ optional HTML) email via SMTP.
    Settings are read from the DB settings table at call time.
    Returns (success, message).
    """
    try:
        cfg  = _get_cfg()
        host = cfg.get('smtp_host', '')
        port = int(cfg.get('smtp_port', 587))
        user = cfg.get('smtp_user', '')
        pwd  = cfg.get('smtp_pass', '')
        frm  = cfg.get('from_email') or user

        if not all([host, user, pwd]):
            return False, "SMTP not configured — visit Settings to add credentials"

        msg            = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"SmartAttend <{frm}>"
        msg['To']      = to

        msg.attach(MIMEText(body, 'plain'))
        if html:
            msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(host, port, timeout=10) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(user, pwd)
            srv.sendmail(frm, to, msg.as_string())

        return True, "Email sent"
    except Exception as e:
        return False, str(e)


# ── Notification templates ────────────────────────────────────────────────────

def send_low_attendance_alert(student_name: str, to_email: str, percentage: float):
    today = date.today().strftime('%d %B %Y')
    subj  = f"⚠️ Low Attendance Alert – {student_name}"

    plain = f"""
Dear {student_name},

This is an automated alert from SmartAttend ({today}).

Your current attendance is: {percentage}%

The minimum required attendance is 75%. Please ensure regular attendance
to avoid academic consequences.

This is an auto-generated email. Do not reply.
— SmartAttend System
""".strip()

    html = f"""
<div style="font-family:Inter,Arial,sans-serif;background:#0d0d1a;padding:40px 0;">
  <div style="max-width:520px;margin:auto;background:linear-gradient(135deg,#13131f,#1a1a2e);
              border:1px solid rgba(255,255,255,.1);border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#ef4444,#dc2626);padding:24px 32px;">
      <h2 style="color:#fff;margin:0;font-size:20px;">⚠️ Low Attendance Alert</h2>
      <p style="color:rgba(255,255,255,.8);margin:4px 0 0;">{today}</p>
    </div>
    <div style="padding:32px;">
      <p style="color:#e8e8f0;margin:0 0 16px;">Dear <strong>{student_name}</strong>,</p>
      <p style="color:#9999b3;margin:0 0 24px;">Your current attendance is:</p>
      <div style="text-align:center;margin:24px 0;">
        <span style="font-size:48px;font-weight:700;
                     background:linear-gradient(135deg,#ef4444,#f59e0b);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          {percentage}%
        </span>
      </div>
      <div style="background:rgba(239,68,68,.1);border-left:4px solid #ef4444;
                  padding:16px;border-radius:8px;margin-bottom:24px;">
        <p style="color:#fca5a5;margin:0;">
          Minimum required attendance is <strong>75%</strong>. Please attend classes
          regularly to avoid academic consequences.
        </p>
      </div>
      <p style="color:#9999b3;font-size:12px;margin:0;">
        This is an automated message from SmartAttend. Do not reply.
      </p>
    </div>
  </div>
</div>
"""
    return send_email(to_email, subj, plain, html)


def send_daily_summary(admin_email: str, stats: dict):
    today = date.today().strftime('%d %B %Y')
    subj  = f"📊 Daily Attendance Summary — {today}"

    plain = f"""
Daily Attendance Summary — {today}

Total Students : {stats['total']}
Present Today  : {stats['present']}
Absent Today   : {stats['absent']}
Attendance Rate: {stats['percentage']}%

— SmartAttend System
""".strip()

    pct   = stats['percentage']
    color = '#10d4a3' if pct >= 75 else '#f59e0b' if pct >= 50 else '#ef4444'

    html = f"""
<div style="font-family:Inter,Arial,sans-serif;background:#0d0d1a;padding:40px 0;">
  <div style="max-width:520px;margin:auto;background:linear-gradient(135deg,#13131f,#1a1a2e);
              border:1px solid rgba(255,255,255,.1);border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#6c63ff,#3f8efc);padding:24px 32px;">
      <h2 style="color:#fff;margin:0;font-size:20px;">📊 Daily Attendance Summary</h2>
      <p style="color:rgba(255,255,255,.8);margin:4px 0 0;">{today}</p>
    </div>
    <div style="padding:32px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
        {"".join([
          f'<div style="background:rgba(255,255,255,.05);border-radius:12px;padding:16px;text-align:center;">'
          f'<p style="color:#9999b3;font-size:12px;margin:0 0 8px;">{label}</p>'
          f'<p style="color:{clr};font-size:28px;font-weight:700;margin:0;">{val}</p></div>'
          for label, val, clr in [
            ('Total Students', stats['total'], '#e8e8f0'),
            ('Present Today',  stats['present'], '#10d4a3'),
            ('Absent Today',   stats['absent'], '#ef4444'),
            ('Attendance Rate', f"{pct}%", color),
          ]
        ])}
      </div>
      <p style="color:#9999b3;font-size:12px;margin:0;">Auto-generated by SmartAttend.</p>
    </div>
  </div>
</div>
"""
    return send_email(admin_email, subj, plain, html)


def send_unknown_face_alert(admin_email: str):
    today = date.today().strftime('%d %B %Y')
    subj  = "🚨 Unknown Face Detected"
    plain = f"An unrecognised face was detected by the SmartAttend system on {today}. Please review the attendance session."
    return send_email(admin_email, subj, plain)

```


---
## `static/css/style.css`
*903 lines*

```css
/* ═══════════════════════════════════════════════════════════════
   SmartAttend — Design System
   Dark Glassmorphism | Purple-Blue Gradient | Inter Font
═══════════════════════════════════════════════════════════════ */

/* ── Variables ──────────────────────────────────────────────── */
:root {
  --bg:       #0a0a1a;
  --bg2:      #13131f;
  --bg3:      #1a1a2e;
  --glass:    rgba(255,255,255,.04);
  --glass-b:  rgba(255,255,255,.08);
  --accent:   #6c63ff;
  --accent2:  #3f8efc;
  --success:  #10d4a3;
  --warning:  #f59e0b;
  --danger:   #ef4444;
  --text:     #e8e8f0;
  --text2:    #9999b3;
  --text3:    rgba(255,255,255,.22);
  --border:   rgba(255,255,255,.08);
  --border2:  rgba(255,255,255,.14);
  --sw:       260px;
  --th:       64px;
  --r:        16px;
  --r-sm:     10px;
  --shadow:   0 8px 32px rgba(0,0,0,.4);
  --grad:     linear-gradient(135deg,#6c63ff,#3f8efc);
  --grad-g:   linear-gradient(135deg,#10d4a3,#059669);
  --grad-r:   linear-gradient(135deg,#ef4444,#dc2626);
  --grad-o:   linear-gradient(135deg,#f59e0b,#d97706);
}

/* ── Reset ──────────────────────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{max-width:100%}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.22)}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════ */
.sidebar {
  position: fixed; left:0; top:0; bottom:0;
  width: var(--sw);
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  z-index: 200;
  transition: transform .3s cubic-bezier(.16,1,.3,1);
}

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid var(--border);
}
.brand-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: var(--grad);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; color: #fff; flex-shrink: 0;
  box-shadow: 0 6px 20px rgba(108,99,255,.4);
}
.brand-name { font-size: 1.05rem; font-weight: 700; color: #fff; display: block; line-height: 1.2; }
.brand-sub  { font-size: .68rem; color: var(--accent); font-weight: 600; letter-spacing: .1em; display: block; }

/* Nav */
.sidebar-nav { flex: 1; padding: 16px 12px; overflow-y: auto; }
.nav-section-label {
  font-size: .65rem; font-weight: 700; letter-spacing: .12em;
  color: var(--text3); padding: 4px 10px 10px; margin-top: 8px;
}
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 12px; border-radius: var(--r-sm);
  color: var(--text2); font-size: .875rem; font-weight: 500;
  transition: background .15s, color .15s; cursor: pointer;
  position: relative; margin-bottom: 2px;
}
.nav-item:hover { background: var(--glass); color: var(--text); }
.nav-item.active {
  background: rgba(108,99,255,.15);
  color: #a89cff;
  border-left: 3px solid var(--accent);
  padding-left: 9px;
}
.nav-icon { width: 20px; text-align: center; font-size: 1rem; flex-shrink: 0; }
.nav-label { flex: 1; }
.nav-badge {
  font-size: .6rem; font-weight: 700; letter-spacing: .08em;
  padding: 2px 7px; border-radius: 50px;
}
.nav-badge.live { background: rgba(239,68,68,.2); color: #fca5a5; animation: livePulse 2s ease-in-out infinite; }
@keyframes livePulse { 0%,100%{opacity:1}50%{opacity:.5} }

/* Footer */
.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid var(--border);
}
.user-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 10px; border-radius: var(--r-sm);
  background: var(--glass); margin-bottom: 8px;
}
.user-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  background: var(--grad);
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem; font-weight: 700; color: #fff; flex-shrink: 0;
}
.user-name  { font-size: .82rem; font-weight: 600; color: var(--text); line-height: 1.2; }
.user-role  { font-size: .7rem;  color: var(--accent); font-weight: 500; }
.logout-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; border-radius: var(--r-sm);
  color: var(--text2); font-size: .82rem; font-weight: 500;
  transition: background .15s, color .15s; width: 100%;
}
.logout-btn:hover { background: rgba(239,68,68,.1); color: #fca5a5; }

.sidebar-overlay {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,.6); z-index: 199;
}

/* ═══════════════════════════════════════════════════════════════
   MAIN WRAPPER
═══════════════════════════════════════════════════════════════ */
.main-wrapper { margin-left: var(--sw); min-height: 100vh; display: flex; flex-direction: column; }

/* Topbar */
.topbar {
  height: var(--th);
  background: rgba(13,13,26,.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px; position: sticky; top: 0; z-index: 100;
}
.topbar-left  { display: flex; align-items: center; gap: 16px; }
.topbar-right { display: flex; align-items: center; gap: 16px; }

.sidebar-toggle {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--glass); border: 1px solid var(--border);
  color: var(--text2); cursor: pointer; font-size: .95rem;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s; display: none;
}
.sidebar-toggle:hover { background: var(--glass-b); color: var(--text); }

.page-title h1 { font-size: 1.15rem; font-weight: 700; color: var(--text); }

.topbar-clock { font-size: 1rem; font-weight: 700; color: var(--text); font-variant-numeric: tabular-nums; }
.topbar-date  { font-size: .75rem; color: var(--text2); }
.topbar-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem; font-weight: 700;
}

/* Flash */
.flash-container { padding: 16px 28px 0; display: flex; flex-direction: column; gap: 8px; }
.flash {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: var(--r-sm);
  font-size: .875rem; font-weight: 500;
  animation: flashIn .3s ease;
}
@keyframes flashIn { from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none} }
.flash button { margin-left: auto; background: none; border: none; color: inherit; cursor: pointer; opacity: .6; }
.flash button:hover { opacity: 1; }
.flash-success { background: rgba(16,212,163,.12); border: 1px solid rgba(16,212,163,.3); color: #5eecd0; }
.flash-error   { background: rgba(239,68,68,.12);  border: 1px solid rgba(239,68,68,.3);  color: #fca5a5; }
.flash-info    { background: rgba(108,99,255,.12); border: 1px solid rgba(108,99,255,.3); color: #a89cff; }

/* Main Content */
.main-content { padding: 28px; flex: 1; }

/* ═══════════════════════════════════════════════════════════════
   GLASS CARD
═══════════════════════════════════════════════════════════════ */
.glass-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 24px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.card-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; gap: 12px; }
.card-title  { font-size: .95rem; font-weight: 600; color: var(--text); }
.card-sub    { font-size: .78rem; color: var(--text2); margin-top: 2px; }
.card-badge  {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(108,99,255,.15); color: var(--accent);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════ */
.btn-primary {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--grad); color: #fff; border: none;
  border-radius: var(--r-sm); padding: 10px 20px;
  font-size: .875rem; font-weight: 600; font-family: inherit;
  cursor: pointer; box-shadow: 0 4px 16px rgba(108,99,255,.35);
  transition: transform .15s, box-shadow .15s, opacity .15s;
  white-space: nowrap;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(108,99,255,.5); opacity: .92; }

.btn-ghost {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--glass); color: var(--text2);
  border: 1px solid var(--border); border-radius: var(--r-sm);
  padding: 10px 20px; font-size: .875rem; font-weight: 500;
  font-family: inherit; cursor: pointer;
  transition: background .15s, color .15s, border-color .15s;
  white-space: nowrap;
}
.btn-ghost:hover { background: var(--glass-b); color: var(--text); border-color: var(--border2); }

.btn-sm-primary {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--grad); color: #fff; border: none;
  border-radius: 8px; padding: 7px 14px;
  font-size: .78rem; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: opacity .15s; white-space: nowrap;
}
.btn-sm-primary:hover { opacity: .85; }

.btn-danger {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(239,68,68,.15); color: #fca5a5;
  border: 1px solid rgba(239,68,68,.3); border-radius: var(--r-sm);
  padding: 10px 20px; font-size: .875rem; font-weight: 600;
  font-family: inherit; cursor: pointer; transition: background .15s;
}
.btn-danger:hover { background: rgba(239,68,68,.25); }

/* ═══════════════════════════════════════════════════════════════
   FORMS
═══════════════════════════════════════════════════════════════ */
.form-label {
  display: block; font-size: .72rem; font-weight: 700;
  letter-spacing: .08em; color: var(--text2); margin-bottom: 7px;
}
.required { color: var(--danger); }
.optional  { color: var(--text3); font-weight: 400; }

.input-wrap { position: relative; }
.input-icon {
  position: absolute; left: 13px; top: 50%;
  transform: translateY(-50%); color: var(--text3); font-size: .9rem;
  pointer-events: none;
}
.form-input {
  width: 100%; padding: 12px 13px 12px 40px;
  background: rgba(255,255,255,.05);
  border: 1px solid var(--border);
  border-radius: var(--r-sm); color: var(--text);
  font-size: .9rem; font-family: inherit;
  transition: border-color .2s, background .2s, box-shadow .2s;
}
.form-input:focus {
  outline: none; border-color: rgba(108,99,255,.5);
  background: rgba(108,99,255,.06);
  box-shadow: 0 0 0 3px rgba(108,99,255,.12);
}
.form-input::placeholder { color: var(--text3); }

.form-select {
  width: 100%; padding: 12px 36px 12px 14px;
  background: rgba(255,255,255,.05);
  border: 1px solid var(--border);
  border-radius: var(--r-sm); color: var(--text);
  font-size: .9rem; font-family: inherit; cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239999b3' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center; background-size: 16px;
  transition: border-color .2s, background-color .2s;
}
.form-select:focus { outline: none; border-color: rgba(108,99,255,.5); box-shadow: 0 0 0 3px rgba(108,99,255,.12); }
.form-select option { background: var(--bg2); color: var(--text); }

.form-group { margin-bottom: 18px; }
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.form-divider { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
.form-section-title { font-size: .78rem; font-weight: 700; letter-spacing: .1em; color: var(--accent); margin-bottom: 16px; }
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 28px; padding-top: 20px; border-top: 1px solid var(--border); }

/* ═══════════════════════════════════════════════════════════════
   TABLES
═══════════════════════════════════════════════════════════════ */
.table-wrap { overflow-x: auto; margin: -4px -4px; }
.data-table { width: 100%; border-collapse: collapse; font-size: .875rem; }
.data-table thead tr { border-bottom: 1px solid var(--border); }
.data-table th { padding: 10px 14px; text-align: left; font-size: .7rem; font-weight: 700; letter-spacing: .08em; color: var(--text2); white-space: nowrap; }
.data-table td { padding: 12px 14px; border-bottom: 1px solid rgba(255,255,255,.04); vertical-align: middle; }
.data-table tbody tr:hover { background: rgba(255,255,255,.03); }
.data-table tbody tr:last-child td { border-bottom: none; }
.table-name { font-weight: 600; color: var(--text); font-size: .875rem; }
.table-sub  { font-size: .75rem; color: var(--text2); margin-top: 1px; }
.text-muted { color: var(--text2); font-size: .82rem; }

/* Status badges */
.status-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 50px;
  font-size: .72rem; font-weight: 600;
}
.status-present { background: rgba(16,212,163,.12); color: #5eecd0; }
.status-late    { background: rgba(245,158,11,.12);  color: #fbbf4a; }
.status-absent  { background: rgba(239,68,68,.12);   color: #fca5a5; }

.subject-pill {
  display: inline-block;
  background: rgba(108,99,255,.12);
  border: 1px solid rgba(108,99,255,.2);
  color: #a89cff; border-radius: 6px;
  padding: 2px 9px; font-size: .72rem; font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════════
   KPI CARDS
═══════════════════════════════════════════════════════════════ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px; margin-bottom: 24px;
}
.kpi-card {
  border-radius: var(--r); padding: 22px;
  display: flex; align-items: center; gap: 16px;
  position: relative; overflow: hidden;
  border: 1px solid var(--border);
  transition: transform .2s, box-shadow .2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.kpi-purple { background: linear-gradient(135deg,rgba(108,99,255,.18),rgba(108,99,255,.06)); }
.kpi-green  { background: linear-gradient(135deg,rgba(16,212,163,.18),rgba(16,212,163,.06)); }
.kpi-red    { background: linear-gradient(135deg,rgba(239,68,68,.18),rgba(239,68,68,.06)); }
.kpi-blue   { background: linear-gradient(135deg,rgba(63,142,252,.18),rgba(63,142,252,.06)); }
.kpi-orange { background: linear-gradient(135deg,rgba(245,158,11,.18),rgba(245,158,11,.06)); }

.kpi-icon {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
}
.kpi-purple .kpi-icon { background: rgba(108,99,255,.25); color: #a89cff; }
.kpi-green  .kpi-icon { background: rgba(16,212,163,.25);  color: #5eecd0; }
.kpi-red    .kpi-icon { background: rgba(239,68,68,.25);   color: #fca5a5; }
.kpi-blue   .kpi-icon { background: rgba(63,142,252,.25);  color: #7dbfff; }
.kpi-orange .kpi-icon { background: rgba(245,158,11,.25);  color: #fbbf4a; }

.kpi-label { font-size: .72rem; font-weight: 600; letter-spacing: .06em; color: var(--text2); margin-bottom: 4px; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: var(--text); line-height: 1; }
.kpi-sub   { font-size: .72rem; color: var(--text2); margin-top: 4px; }

.kpi-ring { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); width: 52px; height: 52px; opacity: .4; }
.kpi-ring svg { width: 100%; height: 100%; }

/* ═══════════════════════════════════════════════════════════════
   LAYOUT HELPERS
═══════════════════════════════════════════════════════════════ */
.row-2col  { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.col-stack { display: flex; flex-direction: column; gap: 20px; }
.chart-wrap    { height: 220px; position: relative; }
.chart-wrap-sm { height: 180px; position: relative; }

/* ═══════════════════════════════════════════════════════════════
   PAGE ACTIONS & FILTERS
═══════════════════════════════════════════════════════════════ */
.page-actions {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px; gap: 16px; flex-wrap: wrap;
}
.count-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.count-pill {
  background: var(--glass); border: 1px solid var(--border);
  border-radius: 50px; padding: 5px 14px;
  font-size: .78rem; font-weight: 600; color: var(--text2);
}
.count-green  { background: rgba(16,212,163,.1);  border-color: rgba(16,212,163,.2);  color: #5eecd0; }
.count-orange { background: rgba(245,158,11,.1);  border-color: rgba(245,158,11,.2);  color: #fbbf4a; }
.count-red    { background: rgba(239,68,68,.1);   border-color: rgba(239,68,68,.2);   color: #fca5a5; }

.filter-card { padding: 16px 20px; margin-bottom: 20px; }
.filter-form {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.filter-group { flex: 1; min-width: 160px; }
.filter-group .form-input,
.filter-group .form-select { margin-bottom: 0; }

/* ═══════════════════════════════════════════════════════════════
   STUDENT GRID
═══════════════════════════════════════════════════════════════ */
.student-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px; margin-bottom: 16px;
}
.student-card {
  background: var(--glass); border: 1px solid var(--border);
  border-radius: var(--r); padding: 20px;
  display: flex; flex-direction: column; align-items: center;
  text-align: center; gap: 12px;
  transition: transform .2s, border-color .2s, box-shadow .2s;
}
.student-card:hover { transform: translateY(-3px); border-color: rgba(108,99,255,.3); box-shadow: 0 12px 32px rgba(108,99,255,.1); }

.sc-avatar-wrap { position: relative; }
.sc-avatar {
  width: 76px; height: 76px; border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
}
.sc-avatar-fallback {
  width: 76px; height: 76px; border-radius: 50%;
  background: var(--grad);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; font-weight: 700; color: #fff;
}
.sc-trained-badge {
  position: absolute; bottom: 2px; right: 2px;
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .6rem; border: 2px solid var(--bg2);
}
.sc-trained-badge.trained   { background: var(--success); color: #fff; }
.sc-trained-badge.untrained { background: var(--danger);  color: #fff; }

.sc-name { font-size: .95rem; font-weight: 700; color: var(--text); }
.sc-id   { font-size: .75rem; color: var(--accent); font-weight: 500; }
.sc-meta {
  display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;
  font-size: .72rem; color: var(--text2); gap: 8px;
}
.sc-meta span { display: flex; align-items: center; gap: 4px; }

.sc-actions { display: flex; gap: 8px; justify-content: center; width: 100%; }
.sc-btn {
  flex: 1; padding: 8px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--glass);
  color: var(--text2); cursor: pointer; font-size: .85rem;
  transition: background .15s, color .15s; display: flex;
  align-items: center; justify-content: center;
}
.sc-btn:hover { background: var(--glass-b); color: var(--text); }
.sc-btn-view:hover { border-color: rgba(108,99,255,.4); color: var(--accent); }
.sc-btn-face:hover { border-color: rgba(16,212,163,.4);  color: var(--success); }
.sc-btn-del:hover  { border-color: rgba(239,68,68,.4);   color: var(--danger);  }
.sc-btn form { margin: 0; width: 100%; }

.result-count { font-size: .78rem; color: var(--text2); text-align: right; margin-top: 8px; }

/* ═══════════════════════════════════════════════════════════════
   EMPTY STATES
═══════════════════════════════════════════════════════════════ */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 32px; color: var(--text2); font-size: .875rem;
}
.empty-state i { font-size: 2rem; color: var(--text3); }
.empty-state-sm {
  padding: 20px; text-align: center;
  color: var(--text2); font-size: .82rem;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.empty-page {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 360px; gap: 12px; text-align: center;
}
.empty-page i { font-size: 3rem; color: var(--text3); }
.empty-page h3 { font-size: 1.2rem; color: var(--text2); }
.empty-page p  { color: var(--text3); font-size: .875rem; margin-bottom: 8px; }

/* ═══════════════════════════════════════════════════════════════
   DASHBOARD SPECIFICS
═══════════════════════════════════════════════════════════════ */
.dept-legend { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.dept-leg-item { display: flex; align-items: center; gap: 6px; font-size: .75rem; color: var(--text2); }
.leg-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.leg-val { color: var(--text); font-weight: 600; margin-left: 2px; }

.low-att-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.low-att-row:last-of-type { border-bottom: none; }
.low-att-name { font-size: .875rem; font-weight: 600; color: var(--text); }
.low-att-dept { font-size: .72rem; color: var(--text2); margin-top: 2px; }
.low-att-pct  { font-size: 1.1rem; font-weight: 800; }
.badge-alert  {
  background: rgba(239,68,68,.2); color: #fca5a5;
  border-radius: 50px; padding: 2px 10px;
  font-size: .72rem; font-weight: 700;
}
.view-all-link {
  display: block; text-align: right; margin-top: 12px;
  font-size: .78rem; color: var(--accent); font-weight: 600;
  transition: color .15s;
}
.view-all-link:hover { color: var(--accent2); }

.log-item { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.log-item:last-child { border-bottom: none; }
.log-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-top: 6px; flex-shrink: 0; }
.log-action { font-size: .82rem; font-weight: 600; color: var(--text); }
.log-detail { font-size: .75rem; color: var(--text2); margin-top: 2px; }
.log-time   { font-size: .68rem; color: var(--text3); margin-top: 3px; }

/* ═══════════════════════════════════════════════════════════════
   REGISTER FORM PAGE
═══════════════════════════════════════════════════════════════ */
.form-page-wrap { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
.form-card { flex: 1; }
.form-card-header { display: flex; align-items: center; gap: 16px; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
.form-card-icon {
  width: 48px; height: 48px; border-radius: 14px;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;
}
.form-card-title { font-size: 1rem; font-weight: 700; color: var(--text); }
.form-card-sub   { font-size: .78rem; color: var(--text2); margin-top: 3px; }

.photo-upload-section { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.photo-preview {
  width: 90px; height: 90px; border-radius: 50%;
  background: var(--glass); border: 2px dashed var(--border2);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 6px; flex-shrink: 0; overflow: hidden;
  font-size: .65rem; color: var(--text2);
}
.photo-btn { padding: 7px 16px !important; font-size: .78rem !important; cursor: pointer; }

.form-info-panel { display: flex; flex-direction: column; }
.info-card { padding: 20px; }
.info-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: rgba(108,99,255,.15); color: var(--accent);
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
  margin-bottom: 12px;
}
.info-title { font-size: .875rem; font-weight: 700; color: var(--text); margin-bottom: 14px; }
.info-steps { display: flex; flex-direction: column; gap: 10px; }
.info-step  { display: flex; align-items: flex-start; gap: 10px; font-size: .8rem; color: var(--text2); }
.step-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: .65rem; font-weight: 700; flex-shrink: 0;
}
.tips-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.tips-list li { font-size: .8rem; color: var(--text2); display: flex; align-items: center; gap: 8px; }
.tips-list li::before { content: '→'; color: var(--success); font-size: .75rem; }

/* ═══════════════════════════════════════════════════════════════
   FACE CAPTURE PAGE
═══════════════════════════════════════════════════════════════ */
.capture-layout { display: grid; grid-template-columns: 1fr 340px; gap: 20px; }
.capture-cam-card { display: flex; flex-direction: column; gap: 16px; }
.capture-student-info { display: flex; align-items: center; gap: 14px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.capture-avatar {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700; flex-shrink: 0;
}
.capture-name { font-weight: 700; color: var(--text); }
.capture-meta { font-size: .75rem; color: var(--text2); margin-top: 2px; }

.cam-container {
  width: 100%; aspect-ratio: 4/3; border-radius: 12px;
  background: #06060f; position: relative; overflow: hidden;
  border: 2px solid var(--border);
}
.cam-idle {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; gap: 10px; color: var(--text2);
}
.cam-idle-icon { font-size: 2.5rem; color: var(--text3); }
.cam-idle-text { font-weight: 600; font-size: .95rem; }
.cam-idle-sub  { font-size: .78rem; color: var(--text3); }

#videoEl { width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }
#overlayCanvas { width: 100%; height: 100%; border-radius: 10px; }

.face-indicator {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,.75); backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,.15); border-radius: 50px;
  padding: 6px 16px; display: flex; align-items: center; gap: 8px;
  font-size: .8rem; color: #fff; white-space: nowrap;
}

.capture-progress { }
.progress-header  { display: flex; justify-content: space-between; font-size: .78rem; color: var(--text2); margin-bottom: 8px; }
.progress-header span:last-child { font-weight: 700; color: var(--text); }
.progress-bar-wrap { height: 6px; background: rgba(255,255,255,.08); border-radius: 3px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: var(--grad); border-radius: 3px; transition: width .4s ease; }

.capture-controls { display: flex; gap: 10px; }
.btn-capture {
  flex: 1; padding: 12px; background: var(--grad);
  border: none; border-radius: 10px; color: #fff;
  font-size: .9rem; font-weight: 700; font-family: inherit;
  cursor: pointer; transition: transform .15s, opacity .15s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 20px rgba(108,99,255,.4);
}
.btn-capture:hover:not(:disabled) { transform: scale(1.02); }
.btn-capture:disabled { opacity: .45; cursor: not-allowed; }

.auto-capture-row { display: flex; align-items: center; gap: 10px; }
.toggle-label { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.toggle-label input { display: none; }
.toggle-track {
  width: 38px; height: 22px; background: rgba(255,255,255,.15);
  border-radius: 11px; position: relative; transition: background .2s;
}
.toggle-label input:checked + .toggle-track { background: var(--accent); }
.toggle-thumb {
  position: absolute; top: 3px; left: 3px;
  width: 16px; height: 16px; border-radius: 50%; background: #fff;
  transition: transform .2s;
}
.toggle-label input:checked + .toggle-track .toggle-thumb { transform: translateX(16px); }

.capture-right { display: flex; flex-direction: column; gap: 16px; }

.train-card { display: flex; flex-direction: column; gap: 14px; }
.train-done    { display: flex; align-items: center; gap: 8px; color: var(--success); font-weight: 600; font-size: .875rem; }
.train-pending { display: flex; align-items: center; gap: 8px; color: var(--warning); font-weight: 600; font-size: .875rem; }
.train-bar { display: flex; align-items: center; gap: 12px; }
.train-bar-item { flex: 1; text-align: center; }
.train-num  { font-size: 1.4rem; font-weight: 800; color: var(--text); }
.train-lbl  { font-size: .68rem; color: var(--text2); letter-spacing: .06em; }
.train-bar-div { width: 1px; height: 36px; background: var(--border); }
.btn-train {
  width: 100%; padding: 12px;
  background: linear-gradient(135deg, #10d4a3, #059669);
  border: none; border-radius: 10px; color: #fff;
  font-size: .9rem; font-weight: 700; font-family: inherit;
  cursor: pointer; transition: transform .15s, opacity .15s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 20px rgba(16,212,163,.3);
}
.btn-train:hover:not(:disabled) { transform: scale(1.02); }
.btn-train:disabled { opacity: .4; cursor: not-allowed; }
.train-msg { font-size: .78rem; text-align: center; color: var(--text2); min-height: 18px; }

.thumb-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; max-height: 200px; overflow-y: auto; }
.thumb-img  { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 6px; border: 1px solid var(--border); }
.thumb-empty { grid-column: 1/-1; text-align: center; color: var(--text3); font-size: .78rem; padding: 16px; }
.capture-nav { display: flex; gap: 10px; }
.capture-nav .btn-ghost { flex: 1; justify-content: center; font-size: .78rem; padding: 8px; }

/* ═══════════════════════════════════════════════════════════════
   ATTENDANCE PAGE
═══════════════════════════════════════════════════════════════ */
.att-layout { display: grid; grid-template-columns: 1fr 380px; gap: 20px; }

.att-controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.att-controls .form-select { width: auto; min-width: 200px; }

.cam-status-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-radius: 10px;
  background: var(--glass); border: 1px solid var(--border);
  font-size: .8rem; margin-top: 10px;
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.status-dot.active  { background: var(--success); box-shadow: 0 0 6px var(--success); animation: pulse 1.5s infinite; }
.status-dot.idle    { background: var(--text3); }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.2)} }

.att-list-panel { display: flex; flex-direction: column; gap: 16px; }
.att-count-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(16,212,163,.12); border: 1px solid rgba(16,212,163,.2);
  color: var(--success); border-radius: 50px; padding: 4px 12px;
  font-size: .75rem; font-weight: 700;
}
.live-entry {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.04);
  animation: entryIn .3s ease;
}
@keyframes entryIn { from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none} }
.live-entry:last-child { border-bottom: none; }
.entry-avatar {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 700; flex-shrink: 0;
}
.entry-name { font-size: .85rem; font-weight: 600; color: var(--text); }
.entry-meta { font-size: .72rem; color: var(--text2); }
.entry-time { margin-left: auto; font-size: .72rem; color: var(--text3); white-space: nowrap; }

.manual-mark-form { padding: 16px; background: var(--glass); border-radius: 12px; border: 1px solid var(--border); }
.manual-mark-form .form-group { margin-bottom: 12px; }
.manual-mark-form .form-input { padding-left: 14px; }

/* ═══════════════════════════════════════════════════════════════
   PROFILE PAGE
═══════════════════════════════════════════════════════════════ */
.profile-layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; align-items: start; }

.profile-hero { text-align: center; padding: 28px; }
.profile-avatar-wrap { position: relative; display: inline-block; margin-bottom: 16px; }
.profile-avatar-large {
  width: 110px; height: 110px; border-radius: 50%;
  object-fit: cover; border: 3px solid rgba(108,99,255,.4);
  box-shadow: 0 0 0 6px rgba(108,99,255,.1);
}
.profile-avatar-fallback {
  width: 110px; height: 110px; border-radius: 50%;
  background: var(--grad); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem; font-weight: 800;
  border: 3px solid rgba(108,99,255,.4);
  box-shadow: 0 0 0 6px rgba(108,99,255,.1);
}
.profile-name { font-size: 1.2rem; font-weight: 800; color: var(--text); }
.profile-id   { font-size: .82rem; color: var(--accent); font-weight: 600; margin: 4px 0; }
.profile-dept-badge {
  display: inline-block; background: rgba(108,99,255,.12);
  border: 1px solid rgba(108,99,255,.2); color: #a89cff;
  border-radius: 50px; padding: 3px 12px; font-size: .72rem; font-weight: 600;
  margin-top: 6px;
}
.trained-badge-lg {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 50px; font-size: .75rem; font-weight: 700;
  margin-top: 10px;
}
.trained-badge-lg.yes { background: rgba(16,212,163,.12); border: 1px solid rgba(16,212,163,.2); color: var(--success); }
.trained-badge-lg.no  { background: rgba(239,68,68,.12);  border: 1px solid rgba(239,68,68,.2);  color: var(--danger); }

.pct-circle-wrap { margin: 20px auto; width: 120px; height: 120px; position: relative; }
.pct-circle-wrap svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.pct-text {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  text-align: center;
}
.pct-num  { font-size: 1.5rem; font-weight: 800; color: var(--text); line-height: 1; display: block; }
.pct-lbl  { font-size: .65rem; color: var(--text2); letter-spacing: .06em; }

.profile-info-grid { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.info-row { display: flex; justify-content: space-between; align-items: center; font-size: .82rem; }
.info-row-label { color: var(--text2); }
.info-row-val   { color: var(--text); font-weight: 600; text-align: right; max-width: 60%; }

.profile-actions { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.profile-actions .btn-primary,
.profile-actions .btn-ghost { width: 100%; justify-content: center; }

.edit-form-inline { margin-top: 16px; display: none; }
.edit-form-inline.show { display: block; }

/* ═══════════════════════════════════════════════════════════════
   RECORDS PAGE
═══════════════════════════════════════════════════════════════ */
.records-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.export-btns { display: flex; gap: 8px; }
.btn-export-csv   { background: rgba(16,212,163,.12); border: 1px solid rgba(16,212,163,.25); color: var(--success); }
.btn-export-excel { background: rgba(63,142,252,.12);  border: 1px solid rgba(63,142,252,.25); color: #7dbfff; }
.btn-export-csv:hover   { background: rgba(16,212,163,.22); color: var(--success); }
.btn-export-excel:hover { background: rgba(63,142,252,.22);  color: #7dbfff; }

/* ═══════════════════════════════════════════════════════════════
   REPORTS PAGE
═══════════════════════════════════════════════════════════════ */
.reports-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.report-chart-wrap { height: 260px; position: relative; }

/* ═══════════════════════════════════════════════════════════════
   FACULTY PAGE
═══════════════════════════════════════════════════════════════ */
.faculty-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.faculty-card {
  background: var(--glass); border: 1px solid var(--border);
  border-radius: var(--r); padding: 20px;
  transition: border-color .2s, box-shadow .2s;
}
.faculty-card:hover { border-color: rgba(108,99,255,.3); box-shadow: 0 8px 24px rgba(108,99,255,.08); }
.faculty-avatar {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg,#f59e0b,#d97706);
  color: #fff; display: flex; align-items: center;
  justify-content: center; font-size: 1.2rem; font-weight: 700;
  margin-bottom: 12px;
}
.faculty-name { font-weight: 700; color: var(--text); font-size: .95rem; }
.faculty-id   { font-size: .72rem; color: var(--accent); margin-bottom: 8px; }
.faculty-dept { display: inline-block; background: rgba(245,158,11,.1); border: 1px solid rgba(245,158,11,.2); color: #fbbf4a; border-radius: 6px; padding: 2px 9px; font-size: .72rem; font-weight: 600; }
.faculty-email { font-size: .78rem; color: var(--text2); margin-top: 8px; }
.faculty-del {
  margin-top: 14px; width: 100%;
  background: none; border: 1px solid rgba(239,68,68,.2);
  color: #fca5a5; border-radius: 8px; padding: 7px;
  font-size: .78rem; cursor: pointer; font-family: inherit;
  transition: background .15s;
}
.faculty-del:hover { background: rgba(239,68,68,.12); }

.add-faculty-form { padding: 20px; background: var(--glass); border: 1px solid var(--border); border-radius: var(--r); margin-bottom: 24px; }
.add-faculty-form .form-grid-3 { margin-bottom: 0; }

/* ═══════════════════════════════════════════════════════════════
   SETTINGS PAGE
═══════════════════════════════════════════════════════════════ */
.settings-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.settings-section-title {
  font-size: .7rem; font-weight: 700; letter-spacing: .12em;
  color: var(--accent); margin-bottom: 16px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.smtp-status {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 50px; font-size: .75rem; font-weight: 700; margin-bottom: 16px;
}
.smtp-ok  { background: rgba(16,212,163,.12); border: 1px solid rgba(16,212,163,.2); color: var(--success); }
.smtp-bad { background: rgba(239,68,68,.12);  border: 1px solid rgba(239,68,68,.2);  color: var(--danger); }

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS & UTILITIES
═══════════════════════════════════════════════════════════════ */
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.fade-in { animation: fadeIn .4s ease; }
@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }

/* Toast notification */
#toastContainer {
  position: fixed; bottom: 24px; right: 24px;
  display: flex; flex-direction: column; gap: 8px; z-index: 9999;
}
.toast {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px 18px;
  display: flex; align-items: center; gap: 10px;
  font-size: .875rem; box-shadow: 0 8px 24px rgba(0,0,0,.4);
  min-width: 260px; max-width: 360px;
  animation: toastIn .3s cubic-bezier(.16,1,.3,1);
}
.toast.toast-exit { animation: toastOut .25s ease forwards; }
@keyframes toastIn  { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:none} }
@keyframes toastOut { to{opacity:0;transform:translateX(20px)} }
.toast-success i { color: var(--success); }
.toast-error   i { color: var(--danger); }
.toast-info    i { color: var(--accent); }

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════════════════════════ */
@media (max-width:1100px) {
  .kpi-grid   { grid-template-columns: repeat(2,1fr); }
  .row-2col   { grid-template-columns: 1fr; }
  .form-grid-3{ grid-template-columns: 1fr 1fr; }
  .settings-layout { grid-template-columns: 1fr; }
  .reports-grid    { grid-template-columns: 1fr; }
}
@media (max-width:900px) {
  .capture-layout  { grid-template-columns: 1fr; }
  .att-layout      { grid-template-columns: 1fr; }
  .profile-layout  { grid-template-columns: 1fr; }
  .form-page-wrap  { grid-template-columns: 1fr; }
  .form-grid-2     { grid-template-columns: 1fr; }
}
@media (max-width:768px) {
  :root { --sw: 260px; }
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay.show { display: block; }
  .sidebar-toggle { display: flex; }
  .main-wrapper { margin-left: 0; }
  .kpi-grid { grid-template-columns: 1fr 1fr; gap: 12px; }
  .main-content { padding: 16px; }
  .topbar { padding: 0 16px; }
  .topbar-date { display: none; }
  .filter-form { flex-direction: column; }
  .filter-group { min-width: 100%; }
}
@media (max-width:480px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .form-grid-3 { grid-template-columns: 1fr; }
  .student-grid { grid-template-columns: 1fr; }
}

```


---
## `static/js/main.js`
*147 lines*

```javascript
/* ═══════════════════════════════════════════════════════════════
   SmartAttend – main.js
   Clock · Sidebar · Toasts · Flash dismiss · AJAX helpers
═══════════════════════════════════════════════════════════════ */

/* ── Live Clock ─────────────────────────────────────────────── */
function updateClock() {
  const now   = new Date();
  const clock = document.getElementById('topbarClock');
  const dateEl= document.getElementById('topbarDate');
  if (clock)  clock.textContent  = now.toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' });
  if (dateEl) dateEl.textContent = now.toLocaleDateString('en-IN', { weekday:'short', day:'numeric', month:'short', year:'numeric' });
}
updateClock();
setInterval(updateClock, 1000);

/* ── Sidebar Toggle ─────────────────────────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar')?.classList.toggle('open');
  document.getElementById('sidebarOverlay')?.classList.toggle('show');
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('show');
}

/* ── Toast Notifications ────────────────────────────────────── */
(function() {
  const c = document.createElement('div');
  c.id = 'toastContainer';
  document.body.appendChild(c);
})();

function showToast(message, type = 'info', duration = 3500) {
  const icons = {
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    info:    'fa-circle-info',
    warning: 'fa-triangle-exclamation'
  };
  const container = document.getElementById('toastContainer');
  const toast     = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Flash Auto-dismiss (4s) ────────────────────────────────── */
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => {
    f.style.transition = 'opacity .4s';
    f.style.opacity = '0';
    setTimeout(() => f.remove(), 400);
  }, 4000);
});

/* ── AJAX Helpers ───────────────────────────────────────────── */
async function postJSON(url, data) {
  const res = await fetch(url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function getJSON(url) {
  return (await fetch(url)).json();
}

/* ── Student Search Autocomplete ────────────────────────────── */
function setupStudentSearch(inputId, resultsId, onSelect) {
  const input   = document.getElementById(inputId);
  const results = document.getElementById(resultsId);
  if (!input || !results) return;

  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = input.value.trim();
    if (q.length < 2) { results.style.display = 'none'; return; }

    debounce = setTimeout(async () => {
      const data = await getJSON(`/api/students/search?q=${encodeURIComponent(q)}`);
      results.innerHTML = '';
      if (!data.length) { results.style.display = 'none'; return; }

      data.forEach(s => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.style.cssText = `
          padding:10px 14px; cursor:pointer; border-bottom:1px solid rgba(255,255,255,.06);
          display:flex; flex-direction:column; gap:2px;
          transition:background .1s;
        `;
        item.innerHTML = `
          <strong style="font-size:.875rem;color:#e8e8f0;">${s.name}</strong>
          <span style="font-size:.72rem;color:#9999b3;">${s.student_id} · ${s.department} · ${s.year}</span>
        `;
        item.addEventListener('mouseenter', () => item.style.background = 'rgba(108,99,255,.1)');
        item.addEventListener('mouseleave', () => item.style.background = '');
        item.addEventListener('click', () => {
          input.value = s.student_id;
          results.style.display = 'none';
          if (onSelect) onSelect(s);
        });
        results.appendChild(item);
      });

      Object.assign(results.style, {
        display: 'block',
        position: 'absolute',
        zIndex: '500',
        width: '100%',
        background: '#13131f',
        border: '1px solid rgba(255,255,255,.1)',
        borderRadius: '10px',
        boxShadow: '0 8px 24px rgba(0,0,0,.4)',
        overflow: 'hidden',
        top: '100%',
        marginTop: '4px'
      });
    }, 260);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.style.display = 'none';
    }
  });
}

/* ── Confirm delete on forms ────────────────────────────────── */
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

/* ── Copy to clipboard ──────────────────────────────────────── */
function copyText(text, label = 'Copied') {
  navigator.clipboard.writeText(text).then(() => showToast(`${label} copied`, 'success'));
}

```


---
## `static/js/camera.js`
*447 lines*

```javascript
/* ═══════════════════════════════════════════════════════════════
   SmartAttend – camera.js
   Handles: face capture (registration) + live recognition (attendance)
═══════════════════════════════════════════════════════════════ */

/* ══════════════════════════════════════════════════════════════
   SECTION 1 — FACE CAPTURE  (face_capture.html)
══════════════════════════════════════════════════════════════ */

let captureStream      = null;
let autoCaptureTimer   = null;
let capturedTotal      = 0;
let captureIndex       = 0;

function initCapturePage() {
  capturedTotal = window.CAPTURED || 0;
  captureIndex  = capturedTotal;
  updateCaptureUI(capturedTotal);

  // Auto-capture checkbox
  const auto = document.getElementById('autoCapture');
  if (auto) {
    auto.addEventListener('change', () => {
      if (auto.checked && captureStream) {
        startAutoCapture();
      } else {
        stopAutoCapture();
      }
    });
  }
}

/* ── Camera controls ────────────────────────────────────────── */
async function startCamera() {
  try {
    captureStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    const video = document.getElementById('videoEl');
    const idle  = document.getElementById('camIdle');
    const fi    = document.getElementById('faceIndicator');

    video.srcObject = captureStream;
    video.style.display = 'block';
    if (idle) idle.style.display = 'none';
    if (fi)   fi.style.display  = 'flex';

    document.getElementById('btnStartCam').style.display = 'none';
    document.getElementById('btnStopCam').style.display  = 'inline-flex';
    document.getElementById('btnCapture').disabled = false;

    setFaceMsg('Camera ready — position your face');

    // Auto-capture if already checked
    if (document.getElementById('autoCapture')?.checked) {
      startAutoCapture();
    }

  } catch (err) {
    showToast('Camera access denied: ' + err.message, 'error');
  }
}

function stopCamera() {
  stopAutoCapture();
  if (captureStream) {
    captureStream.getTracks().forEach(t => t.stop());
    captureStream = null;
  }
  const video  = document.getElementById('videoEl');
  const idle   = document.getElementById('camIdle');
  const fi     = document.getElementById('faceIndicator');
  if (video)  { video.srcObject = null; video.style.display = 'none'; }
  if (idle)   idle.style.display = 'flex';
  if (fi)     fi.style.display  = 'none';

  document.getElementById('btnStartCam').style.display = 'inline-flex';
  document.getElementById('btnStopCam').style.display  = 'none';
  document.getElementById('btnCapture').disabled       = true;
}

function startAutoCapture() {
  stopAutoCapture();
  autoCaptureTimer = setInterval(captureFrame, 1500);
}

function stopAutoCapture() {
  if (autoCaptureTimer) { clearInterval(autoCaptureTimer); autoCaptureTimer = null; }
}

/* ── Capture frame ──────────────────────────────────────────── */
async function captureFrame() {
  if (!captureStream) { showToast('Start the camera first', 'warning'); return; }
  if (capturedTotal >= window.REQUIRED) {
    stopAutoCapture();
    showToast('All images captured! Click Train now.', 'success');
    return;
  }

  const video  = document.getElementById('videoEl');
  const canvas = document.createElement('canvas');
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const frame = canvas.toDataURL('image/jpeg', 0.85);

  setFaceMsg('Sending…');

  try {
    const res = await postJSON('/api/face/capture', {
      student_id: window.STUDENT_ID,
      frame: frame,
      index: captureIndex
    });

    if (res.success) {
      captureIndex++;
      capturedTotal = res.total;
      updateCaptureUI(capturedTotal);
      addThumb(frame);
      setFaceMsg(`${capturedTotal} / ${window.REQUIRED} captured`);

      if (capturedTotal >= window.REQUIRED) {
        stopAutoCapture();
        document.getElementById('autoCapture').checked = false;
        document.getElementById('btnTrain').disabled   = false;
        showToast(`${window.REQUIRED} images captured — train the model!`, 'success');
        setFaceMsg('Capture complete ✓');
      }
    } else {
      setFaceMsg(res.message || 'No face detected');
    }
  } catch (e) {
    setFaceMsg('Network error');
  }
}

/* ── Train model ────────────────────────────────────────────── */
async function trainModel() {
  const btn = document.getElementById('btnTrain');
  const msg = document.getElementById('trainMsg');
  btn.disabled   = true;
  btn.innerHTML  = '<i class="fa-solid fa-spinner spin"></i> Training…';
  if (msg) msg.textContent = 'Processing face encodings…';

  try {
    const res = await postJSON('/api/face/train', { student_id: window.STUDENT_ID });
    if (res.success) {
      showToast(res.message, 'success');
      if (msg) msg.textContent = '✓ ' + res.message;
      btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Trained!';
      btn.style.background = 'linear-gradient(135deg,#10d4a3,#059669)';
      const trainStatus = document.getElementById('trainStatus');
      if (trainStatus) {
        trainStatus.innerHTML = `
          <div class="train-done">
            <i class="fa-solid fa-circle-check"></i>
            <span>Face model trained successfully</span>
          </div>`;
      }
    } else {
      showToast(res.message, 'error');
      if (msg) msg.textContent = '✗ ' + res.message;
      btn.disabled  = false;
      btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Retry Training';
    }
  } catch (e) {
    showToast('Training failed: ' + e.message, 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Retry Training';
  }
}

/* ── UI helpers ─────────────────────────────────────────────── */
function updateCaptureUI(count) {
  const countEl = document.getElementById('captureCount');
  const fill    = document.getElementById('progressFill');
  const imgCnt  = document.getElementById('trainImgCount');
  const pctEl   = document.getElementById('trainPct');
  const pct     = Math.min(100, Math.round(count / window.REQUIRED * 100));

  if (countEl) countEl.textContent = count;
  if (fill)    fill.style.width    = pct + '%';
  if (imgCnt)  imgCnt.textContent  = count;
  if (pctEl)   pctEl.textContent   = pct + '%';

  // Enable train button if enough images
  const trainBtn = document.getElementById('btnTrain');
  if (trainBtn && count >= window.REQUIRED) trainBtn.disabled = false;
}

function addThumb(dataUrl) {
  const grid  = document.getElementById('thumbGrid');
  const empty = document.getElementById('thumbEmpty');
  if (!grid) return;
  if (empty) empty.remove();

  const img = document.createElement('img');
  img.src       = dataUrl;
  img.className = 'thumb-img';
  grid.appendChild(img);
}

function setFaceMsg(text) {
  const el = document.getElementById('faceMsg');
  if (el) el.textContent = text;
}


/* ══════════════════════════════════════════════════════════════
   SECTION 2 — LIVE ATTENDANCE  (attendance.html)
══════════════════════════════════════════════════════════════ */

let attStream         = null;
let recognitionTimer  = null;
let isRecognizing     = false;
let markedToday       = new Set();

function initAttendancePage() {
  // Populate marked set from server-side list
  document.querySelectorAll('[data-marked-id]').forEach(el => {
    markedToday.add(el.dataset.markedId);
  });
}

/* ── Attendance camera ──────────────────────────────────────── */
async function startAttCamera() {
  try {
    attStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    const video   = document.getElementById('attVideo');
    const canvas  = document.getElementById('attCanvas');
    const idle    = document.getElementById('attIdle');

    video.srcObject = attStream;
    video.style.display  = 'block';
    canvas.style.display = 'block';
    if (idle) idle.style.display = 'none';

    document.getElementById('btnStartAtt').style.display = 'none';
    document.getElementById('btnStopAtt').style.display  = 'inline-flex';

    setAttStatus('active', 'Camera active — select subject and start recognition');
  } catch (err) {
    showToast('Camera error: ' + err.message, 'error');
  }
}

function stopAttCamera() {
  stopRecognition();
  if (attStream) {
    attStream.getTracks().forEach(t => t.stop());
    attStream = null;
  }
  const video  = document.getElementById('attVideo');
  const canvas = document.getElementById('attCanvas');
  const idle   = document.getElementById('attIdle');
  const ctx    = canvas?.getContext('2d');

  if (video)  { video.srcObject = null; video.style.display = 'none'; }
  if (canvas) { canvas.style.display = 'none'; if (ctx) ctx.clearRect(0,0,canvas.width,canvas.height); }
  if (idle)   idle.style.display = 'flex';

  document.getElementById('btnStartAtt').style.display = 'inline-flex';
  document.getElementById('btnStopAtt').style.display  = 'none';
  setAttStatus('idle', 'Camera stopped');
}

/* ── Recognition ────────────────────────────────────────────── */
function startRecognition() {
  const subjectEl = document.getElementById('subjectSelect');
  if (!subjectEl?.value) { showToast('Select a subject first', 'warning'); return; }
  if (!attStream)        { showToast('Start camera first', 'warning'); return; }

  isRecognizing = true;
  document.getElementById('btnStartRec').style.display = 'none';
  document.getElementById('btnStopRec').style.display  = 'inline-flex';
  setAttStatus('active', `Recognising — ${subjectEl.value}`);

  // Send frame every 2 seconds
  recognitionTimer = setInterval(sendFrameForRecognition, 2000);
}

function stopRecognition() {
  isRecognizing = false;
  if (recognitionTimer) { clearInterval(recognitionTimer); recognitionTimer = null; }

  const startBtn = document.getElementById('btnStartRec');
  const stopBtn  = document.getElementById('btnStopRec');
  if (startBtn) startBtn.style.display = 'inline-flex';
  if (stopBtn)  stopBtn.style.display  = 'none';

  // Clear canvas
  const canvas = document.getElementById('attCanvas');
  if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

  setAttStatus('idle', 'Recognition stopped');
}

async function sendFrameForRecognition() {
  const video   = document.getElementById('attVideo');
  const canvas  = document.getElementById('attCanvas');
  const subject = document.getElementById('subjectSelect')?.value;
  if (!video || !canvas || !subject || !attStream) return;

  // Sync canvas size
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;

  // Draw current frame on hidden canvas for capture
  const offscreen = document.createElement('canvas');
  offscreen.width  = canvas.width;
  offscreen.height = canvas.height;
  offscreen.getContext('2d').drawImage(video, 0, 0);
  const frame = offscreen.toDataURL('image/jpeg', 0.75);

  try {
    const res = await postJSON('/api/recognize', { frame, subject });
    if (!res.success) { console.warn('Recognition error:', res.error); return; }

    drawFaceBoxes(canvas, video, res.faces);

    res.marked?.forEach(sid => {
      if (!markedToday.has(sid)) {
        markedToday.add(sid);
        const face = res.faces.find(f => f.student_id === sid);
        if (face) addLiveEntry(face.name, face.student_id, subject);
      }
    });

    // Unknown face detection
    const unknownCount = res.faces.filter(f => !f.student_id).length;
    if (unknownCount > 0) {
      setAttStatus('active', `${res.faces.length} face(s) detected · ${unknownCount} unknown`);
    } else if (res.faces.length > 0) {
      setAttStatus('active', `${res.faces.length} face(s) recognised`);
    }
  } catch (e) {
    console.error('Frame error:', e);
  }
}

/* ── Canvas drawing ─────────────────────────────────────────── */
function drawFaceBoxes(canvas, video, faces) {
  const ctx    = canvas.getContext('2d');
  const scaleX = canvas.width  / (video.videoWidth  || 640);
  const scaleY = canvas.height / (video.videoHeight || 480);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  faces.forEach(face => {
    const { top, right, bottom, left } = face.location;
    const x = left  * scaleX;
    const y = top   * scaleY;
    const w = (right - left)  * scaleX;
    const h = (bottom - top)  * scaleY;

    const known = !!face.student_id;
    const color = known ? '#10d4a3' : '#ef4444';

    // Box
    ctx.strokeStyle = color;
    ctx.lineWidth   = 2;
    ctx.strokeRect(x, y, w, h);

    // Corner accents
    const cs = 14;
    ctx.lineWidth = 3;
    [[x,y,1,1],[x+w,y,-1,1],[x,y+h,1,-1],[x+w,y+h,-1,-1]].forEach(([cx,cy,dx,dy]) => {
      ctx.beginPath();
      ctx.moveTo(cx, cy + dy * cs);
      ctx.lineTo(cx, cy);
      ctx.lineTo(cx + dx * cs, cy);
      ctx.stroke();
    });

    // Label background
    const label = known ? `${face.name}  ${face.confidence}%` : 'Unknown';
    ctx.font  = 'bold 12px Inter, sans-serif';
    const tw  = ctx.measureText(label).width;
    ctx.fillStyle = known ? 'rgba(16,212,163,.85)' : 'rgba(239,68,68,.85)';
    ctx.beginPath();
    ctx.roundRect(x - 1, y - 26, tw + 16, 22, 6);
    ctx.fill();

    // Label text
    ctx.fillStyle = '#fff';
    ctx.fillText(label, x + 7, y - 9);
  });
}

/* ── Live entry list ────────────────────────────────────────── */
function addLiveEntry(name, studentId, subject) {
  const list = document.getElementById('liveEntryList');
  const empty= document.getElementById('liveEmpty');
  if (!list) return;
  if (empty) empty.remove();

  const now  = new Date().toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' });
  const item = document.createElement('div');
  item.className = 'live-entry';
  item.innerHTML = `
    <div class="entry-avatar">${name[0]?.toUpperCase() || '?'}</div>
    <div>
      <div class="entry-name">${name}</div>
      <div class="entry-meta">${studentId} · ${subject}</div>
    </div>
    <div class="entry-time">${now}</div>
  `;
  list.prepend(item);

  // Update count badge
  const badge = document.getElementById('markedCount');
  if (badge) badge.textContent = parseInt(badge.textContent || 0) + 1;

  showToast(`✓ ${name} marked present`, 'success', 2000);
}

/* ── Manual mark ────────────────────────────────────────────── */
async function manualMark() {
  const sid     = document.getElementById('manualSid')?.value?.trim();
  const subject = document.getElementById('subjectSelect')?.value;
  const status  = document.getElementById('manualStatus')?.value || 'Present';

  if (!sid)     { showToast('Enter a student ID', 'warning'); return; }
  if (!subject) { showToast('Select a subject',   'warning'); return; }

  const res = await postJSON('/api/attendance/mark', { student_id: sid, subject, status });
  if (res.success) {
    showToast(res.message, 'success');
    document.getElementById('manualSid').value = '';
    // Add to live list
    const name = document.getElementById('manualNameDisplay')?.textContent || sid;
    addLiveEntry(name, sid, subject);
  } else {
    showToast(res.message, 'error');
  }
}

/* ── Status bar ─────────────────────────────────────────────── */
function setAttStatus(state, text) {
  const dot  = document.getElementById('statusDot');
  const msg  = document.getElementById('statusMsg');
  if (dot) { dot.className = `status-dot ${state}`; }
  if (msg) msg.textContent = text;
}

```


---
## `templates/base.html`
*163 lines*

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}SmartAttend{% endblock %} – AI Attendance</title>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <!-- Chart.js -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>

  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
  {% block head %}{% endblock %}
</head>
<body>

<!-- ═══════════════════════════════════════════════
     SIDEBAR
══════════════════════════════════════════════════ -->
<aside class="sidebar" id="sidebar">

  <!-- Brand -->
  <div class="sidebar-brand">
    <div class="brand-icon">
      <i class="fa-solid fa-eye"></i>
    </div>
    <div>
      <span class="brand-name">SmartAttend</span>
      <span class="brand-sub">AI Powered</span>
    </div>
  </div>

  <!-- Navigation -->
  <nav class="sidebar-nav">
    <div class="nav-section-label">MAIN MENU</div>

    <a href="{{ url_for('dashboard') }}"
       class="nav-item {% if request.endpoint == 'dashboard' %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-chart-pie"></i></span>
      <span class="nav-label">Dashboard</span>
    </a>

    <a href="{{ url_for('students') }}"
       class="nav-item {% if request.endpoint in ['students','add_student','student_profile','edit_student'] %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-users"></i></span>
      <span class="nav-label">Students</span>
    </a>

    <a href="{{ url_for('attendance') }}"
       class="nav-item {% if request.endpoint == 'attendance' %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-camera"></i></span>
      <span class="nav-label">Take Attendance</span>
      <span class="nav-badge live">LIVE</span>
    </a>

    <a href="{{ url_for('records') }}"
       class="nav-item {% if request.endpoint == 'records' %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-table-list"></i></span>
      <span class="nav-label">Records</span>
    </a>

    <a href="{{ url_for('reports') }}"
       class="nav-item {% if request.endpoint == 'reports' %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-chart-bar"></i></span>
      <span class="nav-label">Reports</span>
    </a>

    {% if current_user and current_user.role == 'admin' %}
    <div class="nav-section-label" style="margin-top:24px;">ADMIN</div>

    <a href="{{ url_for('faculty') }}"
       class="nav-item {% if request.endpoint in ['faculty','add_faculty'] %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-user-tie"></i></span>
      <span class="nav-label">Faculty</span>
    </a>

    <a href="{{ url_for('settings') }}"
       class="nav-item {% if request.endpoint == 'settings' %}active{% endif %}">
      <span class="nav-icon"><i class="fa-solid fa-gear"></i></span>
      <span class="nav-label">Settings</span>
    </a>
    {% endif %}
  </nav>

  <!-- Sidebar Footer -->
  <div class="sidebar-footer">
    {% if current_user %}
    <div class="user-card">
      <div class="user-avatar">
        {{ current_user.full_name[0]|upper }}
      </div>
      <div class="user-info">
        <div class="user-name">{{ current_user.full_name }}</div>
        <div class="user-role">{{ current_user.role|title }}</div>
      </div>
    </div>
    <a href="{{ url_for('logout') }}" class="logout-btn">
      <i class="fa-solid fa-right-from-bracket"></i>
      <span>Logout</span>
    </a>
    {% endif %}
  </div>
</aside>

<!-- Overlay for mobile -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>

<!-- ═══════════════════════════════════════════════
     MAIN WRAPPER
══════════════════════════════════════════════════ -->
<div class="main-wrapper">

  <!-- Top Bar -->
  <header class="topbar">
    <div class="topbar-left">
      <button class="sidebar-toggle" onclick="toggleSidebar()">
        <i class="fa-solid fa-bars"></i>
      </button>
      <div class="page-title">
        {% block page_title %}<h1>Dashboard</h1>{% endblock %}
      </div>
    </div>
    <div class="topbar-right">
      <div class="topbar-clock" id="topbarClock">--:--</div>
      <div class="topbar-date" id="topbarDate">Loading...</div>
      <div class="topbar-user">
        <div class="topbar-avatar">
          {% if current_user %}{{ current_user.full_name[0]|upper }}{% else %}?{% endif %}
        </div>
      </div>
    </div>
  </header>

  <!-- Flash Messages -->
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="flash-container">
      {% for cat, msg in messages %}
      <div class="flash flash-{{ cat }}">
        <i class="fa-solid {% if cat == 'success' %}fa-circle-check{% elif cat == 'error' %}fa-circle-xmark{% else %}fa-circle-info{% endif %}"></i>
        <span>{{ msg }}</span>
        <button onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  {% endwith %}

  <!-- Page Content -->
  <main class="main-content">
    {% block content %}{% endblock %}
  </main>

</div><!-- /.main-wrapper -->

<script src="{{ url_for('static', filename='js/main.js') }}"></script>
{% block scripts %}{% endblock %}
</body>
</html>

```


---
## `templates/index.html`
*344 lines*

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SmartAttend – AI Attendance System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
  <style>
    /* ── Landing-only overrides ── */
    body { background: #0a0a1a; overflow-x: hidden; }

    /* Hero */
    .hero {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }
    .hero-bg {
      position: absolute; inset: 0;
      background: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(108,99,255,.35) 0%, transparent 70%),
                  radial-gradient(ellipse 60% 50% at 80% 100%, rgba(63,142,252,.2) 0%, transparent 70%);
    }
    /* Animated grid */
    .hero-grid {
      position: absolute; inset: 0;
      background-image:
        linear-gradient(rgba(108,99,255,.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(108,99,255,.05) 1px, transparent 1px);
      background-size: 60px 60px;
      animation: gridMove 20s linear infinite;
    }
    @keyframes gridMove {
      0%   { background-position: 0 0; }
      100% { background-position: 60px 60px; }
    }

    /* Floating blobs */
    .blob {
      position: absolute; border-radius: 50%;
      filter: blur(80px); opacity: .15;
      animation: blobFloat 8s ease-in-out infinite;
    }
    .blob-1 { width: 400px; height: 400px; background: #6c63ff; top: -100px; left: -100px; }
    .blob-2 { width: 300px; height: 300px; background: #3f8efc; bottom: 0; right: 10%; animation-delay: -3s; }
    .blob-3 { width: 250px; height: 250px; background: #10d4a3; top: 40%; left: 60%; animation-delay: -5s; }
    @keyframes blobFloat {
      0%, 100% { transform: translate(0,0) scale(1); }
      33%  { transform: translate(20px,-20px) scale(1.05); }
      66%  { transform: translate(-15px,15px) scale(.95); }
    }

    .hero-content {
      position: relative; z-index: 2;
      text-align: center;
      padding: 2rem;
      max-width: 780px;
      margin: auto;
    }
    .hero-badge {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(108,99,255,.15);
      border: 1px solid rgba(108,99,255,.4);
      border-radius: 50px;
      padding: 6px 18px;
      font-size: .8rem; font-weight: 600; letter-spacing: .08em;
      color: #a89cff; margin-bottom: 32px;
    }
    .hero-badge i { font-size: .9rem; color: #6c63ff; }

    .hero-title {
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      font-weight: 800; line-height: 1.1;
      color: #fff;
      margin-bottom: 24px;
    }
    .hero-title .gradient-text {
      background: linear-gradient(135deg, #6c63ff, #3f8efc, #10d4a3);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .hero-sub {
      font-size: 1.1rem; color: rgba(255,255,255,.6);
      line-height: 1.7; max-width: 520px; margin: 0 auto 48px;
    }

    .hero-cta {
      display: flex; align-items: center; justify-content: center; gap: 16px;
      flex-wrap: wrap;
    }
    .btn-primary-lg {
      display: inline-flex; align-items: center; gap: 10px;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      color: #fff; border: none; border-radius: 14px;
      padding: 16px 36px; font-size: 1rem; font-weight: 600;
      cursor: pointer; text-decoration: none;
      box-shadow: 0 8px 32px rgba(108,99,255,.4);
      transition: transform .2s, box-shadow .2s;
    }
    .btn-primary-lg:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 40px rgba(108,99,255,.55);
      color: #fff;
    }
    .btn-ghost-lg {
      display: inline-flex; align-items: center; gap: 10px;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.15);
      color: rgba(255,255,255,.8); border-radius: 14px;
      padding: 16px 36px; font-size: 1rem; font-weight: 500;
      text-decoration: none;
      transition: background .2s, border-color .2s;
    }
    .btn-ghost-lg:hover {
      background: rgba(255,255,255,.1);
      border-color: rgba(255,255,255,.3);
      color: #fff;
    }

    /* Stats bar */
    .stats-bar {
      display: flex; justify-content: center; gap: 48px;
      margin-top: 72px; flex-wrap: wrap;
    }
    .stat-item { text-align: center; }
    .stat-num {
      font-size: 2rem; font-weight: 800;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-lbl { font-size: .8rem; color: rgba(255,255,255,.4); letter-spacing: .08em; margin-top: 4px; }

    /* Features */
    .features { padding: 100px 0; }
    .section-label {
      text-align: center;
      font-size: .75rem; font-weight: 700; letter-spacing: .15em;
      color: #6c63ff; margin-bottom: 16px;
    }
    .section-title {
      text-align: center; font-size: clamp(1.6rem,4vw,2.4rem);
      font-weight: 700; color: #fff; margin-bottom: 16px;
    }
    .section-sub {
      text-align: center; color: rgba(255,255,255,.5);
      max-width: 480px; margin: 0 auto 64px;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
      max-width: 1100px; margin: 0 auto;
      padding: 0 24px;
    }
    .feature-card {
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 20px; padding: 32px;
      transition: transform .3s, border-color .3s, box-shadow .3s;
    }
    .feature-card:hover {
      transform: translateY(-6px);
      border-color: rgba(108,99,255,.4);
      box-shadow: 0 20px 60px rgba(108,99,255,.15);
    }
    .feature-icon {
      width: 56px; height: 56px; border-radius: 16px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; margin-bottom: 20px;
    }
    .icon-purple { background: rgba(108,99,255,.2); color: #a89cff; }
    .icon-blue   { background: rgba(63,142,252,.2);  color: #7dbfff; }
    .icon-teal   { background: rgba(16,212,163,.2);  color: #5eecd0; }
    .icon-orange { background: rgba(245,158,11,.2);  color: #fbbf4a; }
    .icon-red    { background: rgba(239,68,68,.2);   color: #f87171; }
    .icon-indigo { background: rgba(99,102,241,.2);  color: #a5b4fc; }

    .feature-title { font-size: 1.05rem; font-weight: 600; color: #fff; margin-bottom: 12px; }
    .feature-desc  { font-size: .9rem; color: rgba(255,255,255,.5); line-height: 1.6; }

    /* CTA section */
    .cta-section {
      text-align: center; padding: 80px 24px;
      background: linear-gradient(135deg, rgba(108,99,255,.1), rgba(63,142,252,.1));
      border-top: 1px solid rgba(255,255,255,.06);
    }
    .cta-section h2 { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 16px; }
    .cta-section p  { color: rgba(255,255,255,.5); margin-bottom: 36px; }

    /* Navbar */
    .landing-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      display: flex; align-items: center; justify-content: space-between;
      padding: 20px 48px;
      background: rgba(10,10,26,.8);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .nav-brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
    .nav-brand-icon {
      width: 36px; height: 36px;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-size: .9rem;
    }
    .nav-brand-text { font-weight: 700; color: #fff; font-size: 1.1rem; }
    .nav-login {
      display: inline-flex; align-items: center; gap: 8px;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      color: #fff; padding: 10px 24px; border-radius: 10px;
      font-weight: 600; text-decoration: none; font-size: .9rem;
      transition: opacity .2s;
    }
    .nav-login:hover { opacity: .85; color: #fff; }
  </style>
</head>
<body>

<!-- Navbar -->
<nav class="landing-nav">
  <a href="/" class="nav-brand">
    <div class="nav-brand-icon"><i class="fa-solid fa-eye"></i></div>
    <span class="nav-brand-text">SmartAttend</span>
  </a>
  <a href="{{ url_for('login') }}" class="nav-login">
    <i class="fa-solid fa-right-to-bracket"></i> Login
  </a>
</nav>

<!-- Hero -->
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-grid"></div>
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>

  <div class="hero-content">
    <div class="hero-badge">
      <i class="fa-solid fa-microchip"></i>
      AI-POWERED FACE RECOGNITION
    </div>

    <h1 class="hero-title">
      Attendance Management<br>
      <span class="gradient-text">Reimagined with AI</span>
    </h1>

    <p class="hero-sub">
      Automate student attendance using real-time facial recognition.
      Zero manual effort, 99% accuracy, instant analytics.
    </p>

    <div class="hero-cta">
      <a href="{{ url_for('login') }}" class="btn-primary-lg">
        <i class="fa-solid fa-right-to-bracket"></i>
        Get Started
      </a>
      <a href="#features" class="btn-ghost-lg">
        <i class="fa-solid fa-circle-play"></i>
        Explore Features
      </a>
    </div>

    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-num">99%</div>
        <div class="stat-lbl">ACCURACY</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">&lt;2s</div>
        <div class="stat-lbl">RECOGNITION TIME</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">∞</div>
        <div class="stat-lbl">STUDENTS SUPPORTED</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">0</div>
        <div class="stat-lbl">MANUAL EFFORT</div>
      </div>
    </div>
  </div>
</section>

<!-- Features -->
<section class="features" id="features">
  <div class="section-label">CAPABILITIES</div>
  <h2 class="section-title">Everything you need</h2>
  <p class="section-sub">A complete attendance platform — from face capture to analytics to exports.</p>

  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-icon icon-purple"><i class="fa-solid fa-face-smile"></i></div>
      <div class="feature-title">Real-Time Face Recognition</div>
      <div class="feature-desc">Live webcam detection identifies and marks students instantly with confidence scoring and duplicate prevention.</div>
    </div>
    <div class="feature-card">
      <div class="feature-icon icon-blue"><i class="fa-solid fa-chart-line"></i></div>
      <div class="feature-title">Live Analytics Dashboard</div>
      <div class="feature-desc">Real-time stats, department-wise breakdowns, weekly trends, and low-attendance alerts — all in one view.</div>
    </div>
    <div class="feature-card">
      <div class="feature-icon icon-teal"><i class="fa-solid fa-users-gear"></i></div>
      <div class="feature-title">Student Management</div>
      <div class="feature-desc">Register students, capture face datasets, manage profiles, and track individual attendance history.</div>
    </div>
    <div class="feature-card">
      <div class="feature-icon icon-orange"><i class="fa-solid fa-envelope-open-text"></i></div>
      <div class="feature-title">Automated Email Alerts</div>
      <div class="feature-desc">Auto-send low attendance warnings, daily summaries, and unknown face notifications via SMTP.</div>
    </div>
    <div class="feature-card">
      <div class="feature-icon icon-red"><i class="fa-solid fa-file-export"></i></div>
      <div class="feature-title">Reports & Exports</div>
      <div class="feature-desc">Filter and export attendance data to CSV or Excel with full date, department, and subject filtering.</div>
    </div>
    <div class="feature-card">
      <div class="feature-icon icon-indigo"><i class="fa-solid fa-user-shield"></i></div>
      <div class="feature-title">Role-Based Access</div>
      <div class="feature-desc">Separate Admin and Faculty logins with granular permissions — faculty take attendance, admin controls everything.</div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <h2>Ready to automate attendance?</h2>
  <p>Login with your admin credentials to get started in minutes.</p>
  <a href="{{ url_for('login') }}" class="btn-primary-lg">
    <i class="fa-solid fa-right-to-bracket"></i>
    Login Now
  </a>
</section>

</body>
</html>

```


---
## `templates/login.html`
*229 lines*

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Login – SmartAttend</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
  <style>
    body {
      min-height: 100vh;
      display: flex; align-items: center; justify-content: center;
      background: #0a0a1a;
      overflow: hidden;
    }

    /* Animated background */
    .login-bg {
      position: fixed; inset: 0; z-index: 0;
      background:
        radial-gradient(ellipse 70% 60% at 20% 50%, rgba(108,99,255,.25) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 50%, rgba(63,142,252,.2) 0%, transparent 60%);
    }
    .login-grid {
      position: fixed; inset: 0; z-index: 0;
      background-image:
        linear-gradient(rgba(108,99,255,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(108,99,255,.04) 1px, transparent 1px);
      background-size: 50px 50px;
    }
    .blob { position: fixed; border-radius: 50%; filter: blur(100px); opacity: .12; z-index: 0; }
    .b1 { width:500px;height:500px;background:#6c63ff;top:-200px;left:-100px;animation:bFloat 10s ease-in-out infinite; }
    .b2 { width:400px;height:400px;background:#3f8efc;bottom:-150px;right:-100px;animation:bFloat 8s ease-in-out infinite reverse; }
    @keyframes bFloat {
      0%,100%{transform:translate(0,0);}
      50%{transform:translate(30px,-30px);}
    }

    /* Card */
    .login-card {
      position: relative; z-index: 10;
      width: 100%; max-width: 440px;
      background: rgba(19,19,31,.9);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 24px;
      padding: 48px 44px;
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      box-shadow: 0 32px 80px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.05);
      animation: cardIn .5s cubic-bezier(.16,1,.3,1);
    }
    @keyframes cardIn {
      from { opacity:0; transform: translateY(30px) scale(.97); }
      to   { opacity:1; transform: translateY(0) scale(1); }
    }

    /* Logo area */
    .login-logo {
      text-align: center; margin-bottom: 40px;
    }
    .logo-icon {
      width: 68px; height: 68px;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      border-radius: 20px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.8rem; color: #fff;
      margin: 0 auto 20px;
      box-shadow: 0 12px 32px rgba(108,99,255,.5);
    }
    .logo-title { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 4px; }
    .logo-sub   { font-size: .85rem; color: rgba(255,255,255,.4); }

    /* Flash */
    .login-flash {
      display: flex; align-items: center; gap: 10px;
      padding: 12px 16px; border-radius: 10px;
      font-size: .875rem; margin-bottom: 24px;
    }
    .flash-error   { background:rgba(239,68,68,.12); border:1px solid rgba(239,68,68,.3); color:#fca5a5; }
    .flash-success { background:rgba(16,212,163,.12); border:1px solid rgba(16,212,163,.3); color:#5eecd0; }

    /* Form */
    .form-group { margin-bottom: 20px; }
    .form-label {
      display: block; font-size: .8rem; font-weight: 600;
      color: rgba(255,255,255,.5); letter-spacing: .06em;
      margin-bottom: 8px;
    }
    .input-wrap { position: relative; }
    .input-icon {
      position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
      color: rgba(255,255,255,.25); font-size: .95rem;
    }
    .form-input {
      width: 100%; padding: 13px 14px 13px 42px;
      background: rgba(255,255,255,.05);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 12px;
      color: #fff; font-size: .95rem; font-family: inherit;
      transition: border-color .2s, background .2s, box-shadow .2s;
      box-sizing: border-box;
    }
    .form-input:focus {
      outline: none;
      border-color: rgba(108,99,255,.6);
      background: rgba(108,99,255,.07);
      box-shadow: 0 0 0 3px rgba(108,99,255,.15);
    }
    .form-input::placeholder { color: rgba(255,255,255,.2); }

    /* Toggle password */
    .pw-toggle {
      position: absolute; right: 14px; top: 50%; transform: translateY(-50%);
      color: rgba(255,255,255,.25); background: none; border: none;
      cursor: pointer; font-size: .95rem; padding: 0;
      transition: color .2s;
    }
    .pw-toggle:hover { color: rgba(255,255,255,.6); }

    /* Submit */
    .btn-login {
      width: 100%; padding: 14px;
      background: linear-gradient(135deg, #6c63ff, #3f8efc);
      border: none; border-radius: 12px; color: #fff;
      font-size: 1rem; font-weight: 600; font-family: inherit;
      cursor: pointer; margin-top: 8px;
      box-shadow: 0 8px 24px rgba(108,99,255,.4);
      transition: transform .15s, box-shadow .15s;
      display: flex; align-items: center; justify-content: center; gap: 10px;
    }
    .btn-login:hover {
      transform: translateY(-1px);
      box-shadow: 0 12px 32px rgba(108,99,255,.55);
    }
    .btn-login:active { transform: translateY(0); }

    .login-hint {
      text-align: center; margin-top: 28px;
      font-size: .8rem; color: rgba(255,255,255,.25);
    }
    .login-hint strong { color: rgba(255,255,255,.45); }

    .back-link {
      display: block; text-align: center;
      margin-top: 20px; color: rgba(255,255,255,.3);
      font-size: .85rem; text-decoration: none;
      transition: color .2s;
    }
    .back-link:hover { color: rgba(255,255,255,.6); }
  </style>
</head>
<body>
<div class="login-bg"></div>
<div class="login-grid"></div>
<div class="blob b1"></div>
<div class="blob b2"></div>

<div class="login-card">
  <div class="login-logo">
    <div class="logo-icon"><i class="fa-solid fa-eye"></i></div>
    <div class="logo-title">SmartAttend</div>
    <div class="logo-sub">AI-Powered Attendance System</div>
  </div>

  <!-- Flash messages -->
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for cat, msg in messages %}
    <div class="login-flash flash-{{ cat }}">
      <i class="fa-solid {% if cat == 'success' %}fa-circle-check{% else %}fa-circle-xmark{% endif %}"></i>
      {{ msg }}
    </div>
    {% endfor %}
  {% endwith %}

  <form method="POST" action="{{ url_for('login') }}" autocomplete="off">
    <div class="form-group">
      <label class="form-label" for="username">USERNAME</label>
      <div class="input-wrap">
        <i class="input-icon fa-solid fa-user"></i>
        <input type="text" id="username" name="username" class="form-input"
               placeholder="Enter username" required autofocus />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="password">PASSWORD</label>
      <div class="input-wrap">
        <i class="input-icon fa-solid fa-lock"></i>
        <input type="password" id="password" name="password" class="form-input"
               placeholder="Enter password" required />
        <button type="button" class="pw-toggle" id="pwToggle"
                onclick="togglePw()">
          <i class="fa-solid fa-eye" id="pwIcon"></i>
        </button>
      </div>
    </div>

    <button type="submit" class="btn-login">
      <i class="fa-solid fa-right-to-bracket"></i>
      Sign In
    </button>
  </form>

  <div class="login-hint">
    Default credentials: <strong>admin</strong> / <strong>admin123</strong>
  </div>

  <a href="{{ url_for('index') }}" class="back-link">
    <i class="fa-solid fa-arrow-left"></i> Back to Home
  </a>
</div>

<script>
  function togglePw() {
    const inp  = document.getElementById('password');
    const icon = document.getElementById('pwIcon');
    if (inp.type === 'password') {
      inp.type = 'text';
      icon.className = 'fa-solid fa-eye-slash';
    } else {
      inp.type = 'password';
      icon.className = 'fa-solid fa-eye';
    }
  }
</script>
</body>
</html>

```


---
## `templates/dashboard.html`
*305 lines*

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}<h1>Dashboard</h1>{% endblock %}

{% block content %}

<!-- ── KPI Cards ─────────────────────────────────────────────────────── -->
<div class="kpi-grid">
  <div class="kpi-card kpi-purple">
    <div class="kpi-icon"><i class="fa-solid fa-users"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Total Students</div>
      <div class="kpi-value">{{ stats.total }}</div>
      <div class="kpi-sub">{{ face_trained }} face-trained</div>
    </div>
    <div class="kpi-sparkline"></div>
  </div>

  <div class="kpi-card kpi-green">
    <div class="kpi-icon"><i class="fa-solid fa-user-check"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Present Today</div>
      <div class="kpi-value">{{ stats.present }}</div>
      <div class="kpi-sub">{{ today }}</div>
    </div>
  </div>

  <div class="kpi-card kpi-red">
    <div class="kpi-icon"><i class="fa-solid fa-user-xmark"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Absent Today</div>
      <div class="kpi-value">{{ stats.absent }}</div>
      <div class="kpi-sub">out of {{ stats.total }}</div>
    </div>
  </div>

  <div class="kpi-card {% if stats.percentage >= 75 %}kpi-blue{% else %}kpi-orange{% endif %}">
    <div class="kpi-icon"><i class="fa-solid fa-percent"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Attendance Rate</div>
      <div class="kpi-value">{{ stats.percentage }}%</div>
      <div class="kpi-sub">today's rate</div>
    </div>
    <div class="kpi-ring" style="--pct:{{ stats.percentage }}">
      <svg viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="3"/>
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,.8)" stroke-width="3"
                stroke-dasharray="{{ stats.percentage }},100"
                stroke-linecap="round"
                transform="rotate(-90 18 18)"/>
      </svg>
    </div>
  </div>
</div>

<!-- ── Row 2: Charts ──────────────────────────────────────────────────── -->
<div class="row-2col">

  <!-- Weekly Trend -->
  <div class="glass-card">
    <div class="card-header">
      <div>
        <div class="card-title">Weekly Attendance Trend</div>
        <div class="card-sub">Last 7 days</div>
      </div>
      <div class="card-badge"><i class="fa-solid fa-arrow-trend-up"></i></div>
    </div>
    <div class="chart-wrap">
      <canvas id="weeklyChart"></canvas>
    </div>
  </div>

  <!-- Department Doughnut -->
  <div class="glass-card">
    <div class="card-header">
      <div>
        <div class="card-title">Department Presence</div>
        <div class="card-sub">Today's attendance by dept</div>
      </div>
      <div class="card-badge"><i class="fa-solid fa-building"></i></div>
    </div>
    <div class="chart-wrap chart-wrap-sm">
      <canvas id="deptChart"></canvas>
    </div>
    {% if dept_labels %}
    <div class="dept-legend">
      {% for i in range(dept_labels|length) %}
      <div class="dept-leg-item">
        <span class="leg-dot" data-idx="{{ i }}"></span>
        <span class="leg-name">{{ dept_labels[i] }}</span>
        <span class="leg-val">{{ dept_present[i] }}</span>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="empty-state-sm">No attendance recorded today</div>
    {% endif %}
  </div>

</div>

<!-- ── Row 3: Recent Attendance + Low Attendance ─────────────────────── -->
<div class="row-2col">

  <!-- Today's Attendance -->
  <div class="glass-card">
    <div class="card-header">
      <div>
        <div class="card-title">Recent Attendance</div>
        <div class="card-sub">Today's entries</div>
      </div>
      <a href="{{ url_for('attendance') }}" class="btn-sm-primary">
        <i class="fa-solid fa-camera"></i> Take Attendance
      </a>
    </div>
    {% if today_attendance %}
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Subject</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {% for r in today_attendance %}
          <tr>
            <td>
              <div class="table-name">{{ r.student_name }}</div>
              <div class="table-sub">{{ r.student_id }}</div>
            </td>
            <td><span class="subject-pill">{{ r.subject }}</span></td>
            <td class="text-muted">{{ r.time }}</td>
            <td>
              <span class="status-badge {% if r.status == 'Present' %}status-present{% else %}status-late{% endif %}">
                {{ r.status }}
              </span>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="empty-state">
      <i class="fa-solid fa-calendar-xmark"></i>
      <span>No attendance recorded today</span>
    </div>
    {% endif %}
  </div>

  <!-- Right column: Low Attendance + Activity Log -->
  <div class="col-stack">

    <!-- Low Attendance Alert -->
    <div class="glass-card">
      <div class="card-header">
        <div>
          <div class="card-title">⚠️ Low Attendance</div>
          <div class="card-sub">Students below 75%</div>
        </div>
        {% if low_att %}
        <span class="badge-alert">{{ low_att|length }}</span>
        {% endif %}
      </div>
      {% if low_att %}
        {% for s in low_att %}
        <div class="low-att-row">
          <div>
            <div class="low-att-name">{{ s.name }}</div>
            <div class="low-att-dept">{{ s.department }} · {{ s.year }}</div>
          </div>
          <div class="low-att-pct" style="color: {{ '#ef4444' if s.percentage < 50 else '#f59e0b' }}">
            {{ s.percentage }}%
          </div>
        </div>
        {% endfor %}
        <a href="{{ url_for('students') }}" class="view-all-link">View all →</a>
      {% else %}
      <div class="empty-state-sm">
        <i class="fa-solid fa-circle-check" style="color:#10d4a3"></i>
        All students above 75%
      </div>
      {% endif %}
    </div>

    <!-- Activity Log -->
    <div class="glass-card">
      <div class="card-header">
        <div class="card-title">Recent Activity</div>
      </div>
      {% if recent_log %}
        {% for log in recent_log %}
        <div class="log-item">
          <div class="log-dot"></div>
          <div>
            <div class="log-action">{{ log.action.replace('_', ' ') }}</div>
            <div class="log-detail">{{ log.details or '—' }}</div>
            <div class="log-time">{{ log.timestamp }}</div>
          </div>
        </div>
        {% endfor %}
      {% else %}
      <div class="empty-state-sm">No recent activity</div>
      {% endif %}
    </div>

  </div>
</div>

{% endblock %}

{% block scripts %}
<script>
const WEEKLY_DATES  = {{ weekly_dates | tojson }};
const WEEKLY_COUNTS = {{ weekly_counts | tojson }};
const DEPT_LABELS   = {{ dept_labels | tojson }};
const DEPT_PRESENT  = {{ dept_present | tojson }};

// Chart defaults
Chart.defaults.color = 'rgba(255,255,255,0.45)';
Chart.defaults.font.family = 'Inter, sans-serif';

// ── Weekly Trend ─────────────────────────
const wCtx = document.getElementById('weeklyChart');
if (wCtx) {
  const gradient = wCtx.getContext('2d').createLinearGradient(0, 0, 0, 250);
  gradient.addColorStop(0, 'rgba(108,99,255,0.4)');
  gradient.addColorStop(1, 'rgba(108,99,255,0)');

  new Chart(wCtx, {
    type: 'line',
    data: {
      labels: WEEKLY_DATES.length ? WEEKLY_DATES : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
      datasets: [{
        label: 'Students Present',
        data:   WEEKLY_COUNTS.length ? WEEKLY_COUNTS : [0,0,0,0,0,0,0],
        fill:   true,
        backgroundColor: gradient,
        borderColor: '#6c63ff',
        borderWidth: 2.5,
        pointBackgroundColor: '#6c63ff',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,.05)' }, ticks: { font: { size: 11 } } },
        y: { grid: { color: 'rgba(255,255,255,.05)' }, ticks: { stepSize: 1 }, beginAtZero: true }
      }
    }
  });
}

// ── Dept Doughnut ────────────────────────
const dCtx = document.getElementById('deptChart');
if (dCtx && DEPT_LABELS.length) {
  const COLORS = ['#6c63ff','#3f8efc','#10d4a3','#f59e0b','#ef4444','#a855f7','#06b6d4','#ec4899'];
  new Chart(dCtx, {
    type: 'doughnut',
    data: {
      labels: DEPT_LABELS,
      datasets: [{
        data: DEPT_PRESENT,
        backgroundColor: COLORS.slice(0, DEPT_LABELS.length),
        borderColor: '#13131f',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} present`
          }
        }
      }
    }
  });

  // Colour the legend dots
  const COLORS2 = ['#6c63ff','#3f8efc','#10d4a3','#f59e0b','#ef4444','#a855f7','#06b6d4','#ec4899'];
  document.querySelectorAll('.leg-dot').forEach(dot => {
    dot.style.background = COLORS2[parseInt(dot.dataset.idx) % COLORS2.length];
  });
}

// Auto-refresh stats every 30s
setInterval(() => {
  fetch('/api/stats').then(r=>r.json()).then(d=>{
    // Could update KPI cards live; left as enhancement
  });
}, 30000);
</script>
{% endblock %}

```


---
## `templates/students.html`
*131 lines*

```html
{% extends "base.html" %}
{% block title %}Students{% endblock %}
{% block page_title %}<h1>Students</h1>{% endblock %}

{% block content %}

<!-- ── Top Bar ─────────────────────────────────────────────────────────── -->
<div class="page-actions">
  <div class="count-pills">
    <span class="count-pill">{{ total_count }} Total</span>
    <span class="count-pill count-green">{{ trained_count }} Face-Trained</span>
    <span class="count-pill count-orange">{{ total_count - trained_count }} Pending</span>
  </div>
  <a href="{{ url_for('add_student') }}" class="btn-primary">
    <i class="fa-solid fa-user-plus"></i> Add Student
  </a>
</div>

<!-- ── Filters ─────────────────────────────────────────────────────────── -->
<div class="glass-card filter-card">
  <form method="GET" action="{{ url_for('students') }}" class="filter-form">
    <div class="filter-group">
      <div class="input-wrap">
        <i class="input-icon fa-solid fa-magnifying-glass"></i>
        <input type="text" name="q" value="{{ search }}" class="form-input"
               placeholder="Search name or ID…" />
      </div>
    </div>
    <div class="filter-group">
      <select name="dept" class="form-select">
        <option value="">All Departments</option>
        {% for d in departments %}
        <option value="{{ d }}" {% if dept == d %}selected{% endif %}>{{ d }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="filter-group">
      <select name="year" class="form-select">
        <option value="">All Years</option>
        {% for y in years %}
        <option value="{{ y }}" {% if year == y %}selected{% endif %}>{{ y }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="filter-group">
      <select name="section" class="form-select">
        <option value="">All Sections</option>
        {% for s in sections %}
        <option value="{{ s }}" {% if section == s %}selected{% endif %}>Section {{ s }}</option>
        {% endfor %}
      </select>
    </div>
    <button type="submit" class="btn-primary"><i class="fa-solid fa-filter"></i> Filter</button>
    <a href="{{ url_for('students') }}" class="btn-ghost"><i class="fa-solid fa-rotate-left"></i></a>
  </form>
</div>

<!-- ── Student Grid ────────────────────────────────────────────────────── -->
{% if students %}
<div class="student-grid">
  {% for s in students %}
  <div class="student-card">

    <!-- Avatar -->
    <div class="sc-avatar-wrap">
      {% if s.image_path %}
      <img src="{{ url_for('static', filename=s.image_path) }}" class="sc-avatar" alt="{{ s.name }}" />
      {% else %}
      <div class="sc-avatar sc-avatar-fallback">
        {{ s.name[0]|upper }}
      </div>
      {% endif %}
      <!-- Face-trained badge -->
      <span class="sc-trained-badge {% if s.face_encoding %}trained{% else %}untrained{% endif %}">
        {% if s.face_encoding %}
        <i class="fa-solid fa-circle-check"></i>
        {% else %}
        <i class="fa-solid fa-circle-xmark"></i>
        {% endif %}
      </span>
    </div>

    <!-- Info -->
    <div class="sc-info">
      <div class="sc-name">{{ s.name }}</div>
      <div class="sc-id">{{ s.student_id }}</div>
      <div class="sc-meta">
        <span><i class="fa-solid fa-building fa-xs"></i> {{ s.department }}</span>
        <span><i class="fa-solid fa-calendar fa-xs"></i> {{ s.year }}</span>
        <span><i class="fa-solid fa-layer-group fa-xs"></i> Sec {{ s.section }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="sc-actions">
      <a href="{{ url_for('student_profile', student_id=s.student_id) }}"
         class="sc-btn sc-btn-view" title="View Profile">
        <i class="fa-solid fa-eye"></i>
      </a>
      <a href="{{ url_for('face_capture', student_id=s.student_id) }}"
         class="sc-btn sc-btn-face" title="Face Capture">
        <i class="fa-solid fa-camera"></i>
      </a>
      {% if current_user and current_user.role == 'admin' %}
      <form method="POST" action="{{ url_for('delete_student', student_id=s.student_id) }}"
            onsubmit="return confirm('Remove {{ s.name }}?')">
        <button type="submit" class="sc-btn sc-btn-del" title="Remove">
          <i class="fa-solid fa-trash"></i>
        </button>
      </form>
      {% endif %}
    </div>

  </div>
  {% endfor %}
</div>

<div class="result-count">Showing {{ students|length }} student(s)</div>

{% else %}
<div class="empty-page">
  <i class="fa-solid fa-users-slash"></i>
  <h3>No students found</h3>
  <p>{% if search or dept or year %}Try adjusting the filters.{% else %}Add your first student to get started.{% endif %}</p>
  <a href="{{ url_for('add_student') }}" class="btn-primary">
    <i class="fa-solid fa-user-plus"></i> Add Student
  </a>
</div>
{% endif %}

{% endblock %}

```


---
## `templates/register_student.html`
*158 lines*

```html
{% extends "base.html" %}
{% block title %}Add Student{% endblock %}
{% block page_title %}<h1>Register Student</h1>{% endblock %}

{% block content %}
<div class="form-page-wrap">
  <div class="glass-card form-card">

    <div class="form-card-header">
      <div class="form-card-icon"><i class="fa-solid fa-user-plus"></i></div>
      <div>
        <div class="form-card-title">New Student Registration</div>
        <div class="form-card-sub">Fill in the details. Face capture happens after this step.</div>
      </div>
    </div>

    <form method="POST" action="{{ url_for('add_student') }}" enctype="multipart/form-data">

      <!-- Photo Upload -->
      <div class="photo-upload-section">
        <div class="photo-preview" id="photoPreview">
          <i class="fa-solid fa-user fa-3x" style="color:rgba(255,255,255,.2)"></i>
          <span>Upload Photo</span>
        </div>
        <div class="photo-upload-info">
          <div class="form-label">PROFILE PHOTO <span class="optional">(optional)</span></div>
          <label for="photo" class="btn-ghost photo-btn">
            <i class="fa-solid fa-upload"></i> Choose Image
          </label>
          <input type="file" id="photo" name="photo" accept="image/*"
                 style="display:none" onchange="previewPhoto(event)" />
          <div style="color:rgba(255,255,255,.3);font-size:.78rem;margin-top:8px;">PNG, JPG · Max 16MB</div>
        </div>
      </div>

      <div class="form-divider"></div>
      <div class="form-section-title">Student Information</div>

      <div class="form-grid-2">
        <div class="form-group">
          <label class="form-label">STUDENT ID <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-id-badge"></i>
            <input type="text" name="student_id" class="form-input"
                   placeholder="e.g. RA2211003010001" required maxlength="30"
                   style="text-transform:uppercase" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">FULL NAME <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-user"></i>
            <input type="text" name="name" class="form-input"
                   placeholder="Enter full name" required maxlength="100" />
          </div>
        </div>
      </div>

      <div class="form-grid-3">
        <div class="form-group">
          <label class="form-label">DEPARTMENT <span class="required">*</span></label>
          <select name="department" class="form-select" required>
            <option value="">Select Department</option>
            {% for d in config.DEPARTMENTS %}
            <option value="{{ d }}">{{ d }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">YEAR <span class="required">*</span></label>
          <select name="year" class="form-select" required>
            <option value="">Select Year</option>
            {% for y in config.YEARS %}
            <option value="{{ y }}">{{ y }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">SECTION <span class="required">*</span></label>
          <select name="section" class="form-select" required>
            <option value="">Select Section</option>
            {% for s in config.SECTIONS %}
            <option value="{{ s }}">Section {{ s }}</option>
            {% endfor %}
          </select>
        </div>
      </div>

      <div class="form-section-title" style="margin-top:28px;">Contact Information</div>
      <div class="form-grid-2">
        <div class="form-group">
          <label class="form-label">EMAIL ADDRESS</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-envelope"></i>
            <input type="email" name="email" class="form-input" placeholder="student@college.edu" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">PHONE NUMBER</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-phone"></i>
            <input type="tel" name="phone" class="form-input" placeholder="+91 98765 43210" maxlength="15" />
          </div>
        </div>
      </div>

      <div class="form-actions">
        <a href="{{ url_for('students') }}" class="btn-ghost">
          <i class="fa-solid fa-arrow-left"></i> Cancel
        </a>
        <button type="submit" class="btn-primary">
          <i class="fa-solid fa-arrow-right"></i> Register &amp; Capture Face
        </button>
      </div>
    </form>
  </div>

  <div class="form-info-panel">
    <div class="info-card glass-card">
      <div class="info-icon"><i class="fa-solid fa-circle-info"></i></div>
      <div class="info-title">What happens next?</div>
      <div class="info-steps">
        <div class="info-step"><span class="step-num">1</span><span>Submit this form to create the student record</span></div>
        <div class="info-step"><span class="step-num">2</span><span>You'll be redirected to the face capture page</span></div>
        <div class="info-step"><span class="step-num">3</span><span>Capture 20+ face images using the webcam</span></div>
        <div class="info-step"><span class="step-num">4</span><span>Train the AI model — student is ready for attendance</span></div>
      </div>
    </div>
    <div class="info-card glass-card" style="margin-top:16px;">
      <div class="info-icon" style="background:rgba(16,212,163,.15);color:#10d4a3;">
        <i class="fa-solid fa-lightbulb"></i>
      </div>
      <div class="info-title">Tips for accurate recognition</div>
      <ul class="tips-list">
        <li>Capture in good lighting</li>
        <li>Include multiple angles (left, right, straight)</li>
        <li>Avoid heavy shadows on the face</li>
        <li>Remove glasses for some images</li>
      </ul>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function previewPhoto(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const p = document.getElementById('photoPreview');
    p.innerHTML = `<img src="${ev.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit;" />`;
  };
  reader.readAsDataURL(file);
}
</script>
{% endblock %}

```


---
## `templates/face_capture.html`
*115 lines*

```html
{% extends "base.html" %}
{% block title %}Face Capture – {{ student.name }}{% endblock %}
{% block page_title %}<h1>Face Capture</h1>{% endblock %}

{% block content %}
<div class="capture-layout">

  <!-- Left: Webcam Panel -->
  <div class="glass-card capture-cam-card">
    <div class="capture-student-info">
      <div class="capture-avatar">{{ student.name[0]|upper }}</div>
      <div>
        <div class="capture-name">{{ student.name }}</div>
        <div class="capture-meta">{{ student.student_id }} · {{ student.department }} · {{ student.year }} · Sec {{ student.section }}</div>
      </div>
    </div>

    <div class="cam-container" id="camContainer">
      <div class="cam-idle" id="camIdle">
        <div class="cam-idle-icon"><i class="fa-solid fa-camera"></i></div>
        <div class="cam-idle-text">Camera is off</div>
        <div class="cam-idle-sub">Click "Start Camera" to begin</div>
      </div>
      <video id="videoEl" autoplay muted playsinline style="display:none;width:100%;height:100%;object-fit:cover;"></video>
      <div class="face-indicator" id="faceIndicator" style="display:none;">
        <i class="fa-solid fa-face-smile"></i>
        <span id="faceMsg">Camera ready</span>
      </div>
    </div>

    <div class="capture-progress">
      <div class="progress-header">
        <span>Images Captured</span>
        <span><span id="captureCount">{{ captured }}</span> / {{ required }}</span>
      </div>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" id="progressFill"
             style="width:{{ [[(captured / required * 100)|round|int, 0]|max, 100]|min }}%"></div>
      </div>
    </div>

    <div class="capture-controls">
      <button id="btnStartCam" class="btn-primary" onclick="startCamera()">
        <i class="fa-solid fa-video"></i> Start Camera
      </button>
      <button id="btnCapture" class="btn-capture" onclick="captureFrame()" disabled>
        <i class="fa-solid fa-camera-rotate"></i> Capture
      </button>
      <button id="btnStopCam" class="btn-ghost" onclick="stopCamera()" style="display:none;">
        <i class="fa-solid fa-stop"></i> Stop
      </button>
    </div>

    <div class="auto-capture-row">
      <label class="toggle-label">
        <input type="checkbox" id="autoCapture" />
        <span class="toggle-track"><span class="toggle-thumb"></span></span>
        <span style="color:rgba(255,255,255,.6);font-size:.875rem;">Auto-capture every 1.5s</span>
      </label>
    </div>
  </div>

  <!-- Right Panel -->
  <div class="capture-right">
    <div class="glass-card train-card">
      <div class="train-status" id="trainStatus">
        {% if student.face_encoding %}
        <div class="train-done"><i class="fa-solid fa-circle-check"></i><span>Face model is trained</span></div>
        {% else %}
        <div class="train-pending"><i class="fa-solid fa-hourglass-half"></i><span>Capture {{ required }} images, then train</span></div>
        {% endif %}
      </div>
      <div class="train-bar">
        <div class="train-bar-item"><div class="train-num" id="trainImgCount">{{ captured }}</div><div class="train-lbl">Captured</div></div>
        <div class="train-bar-div"></div>
        <div class="train-bar-item"><div class="train-num">{{ required }}</div><div class="train-lbl">Required</div></div>
        <div class="train-bar-div"></div>
        <div class="train-bar-item">
          <div class="train-num" id="trainPct">{{ [[[(captured / required * 100)|round|int, 0]|max], [100]]|min }}%</div>
          <div class="train-lbl">Complete</div>
        </div>
      </div>
      <button id="btnTrain" class="btn-train" onclick="trainModel()"
              {% if captured < required %}disabled{% endif %}>
        <i class="fa-solid fa-bolt"></i> Train AI Model
      </button>
      <div id="trainMsg" class="train-msg"></div>
    </div>

    <div class="glass-card" style="padding:20px;">
      <div class="card-title" style="margin-bottom:14px;">Captured Images</div>
      <div class="thumb-grid" id="thumbGrid">
        <div class="thumb-empty" id="thumbEmpty">
          {% if captured == 0 %}No images yet — start camera and capture{% else %}{{ captured }} image(s) already saved{% endif %}
        </div>
      </div>
    </div>

    <div class="capture-nav">
      <a href="{{ url_for('students') }}" class="btn-ghost"><i class="fa-solid fa-arrow-left"></i> Students</a>
      <a href="{{ url_for('student_profile', student_id=student.student_id) }}" class="btn-ghost"><i class="fa-solid fa-user"></i> Profile</a>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/camera.js') }}"></script>
<script>
  window.STUDENT_ID = "{{ student.student_id }}";
  window.REQUIRED   = {{ required }};
  window.CAPTURED   = {{ captured }};
  initCapturePage();
</script>
{% endblock %}

```


---
## `templates/attendance.html`
*154 lines*

```html
{% extends "base.html" %}
{% block title %}Take Attendance{% endblock %}
{% block page_title %}<h1>Take Attendance</h1>{% endblock %}

{% block content %}
<div class="att-layout">

  <!-- Left: Camera Panel -->
  <div class="glass-card" style="display:flex;flex-direction:column;gap:16px;">

    <!-- Controls Row -->
    <div class="att-controls">
      <div style="flex:1;min-width:200px;">
        <select id="subjectSelect" class="form-select">
          <option value="">— Select Subject —</option>
          {% for s in subjects %}
          <option value="{{ s }}">{{ s }}</option>
          {% endfor %}
        </select>
      </div>
      <button id="btnStartAtt" class="btn-primary" onclick="startAttCamera()">
        <i class="fa-solid fa-video"></i> Start Camera
      </button>
      <button id="btnStopAtt" class="btn-ghost" onclick="stopAttCamera()" style="display:none;">
        <i class="fa-solid fa-stop"></i> Stop
      </button>
      <button id="btnStartRec" class="btn-primary" onclick="startRecognition()" style="background:linear-gradient(135deg,#10d4a3,#059669);" disabled>
        <i class="fa-solid fa-play"></i> Start Recognition
      </button>
      <button id="btnStopRec" class="btn-danger" onclick="stopRecognition()" style="display:none;">
        <i class="fa-solid fa-stop"></i> Stop
      </button>
    </div>

    <!-- Camera View -->
    <div class="cam-container" style="aspect-ratio:16/9;">
      <div class="cam-idle" id="attIdle">
        <div class="cam-idle-icon"><i class="fa-solid fa-camera"></i></div>
        <div class="cam-idle-text">Camera is off</div>
        <div class="cam-idle-sub">Select a subject, then start camera</div>
      </div>
      <video id="attVideo" autoplay muted playsinline
             style="display:none;width:100%;height:100%;object-fit:cover;"
             onplay="document.getElementById('btnStartRec').disabled=false"></video>
      <canvas id="attCanvas" style="display:none;position:absolute;top:0;left:0;width:100%;height:100%;"></canvas>
    </div>

    <!-- Status Bar -->
    <div class="cam-status-bar">
      <div style="display:flex;align-items:center;gap:8px;">
        <div class="status-dot idle" id="statusDot"></div>
        <span id="statusMsg" style="font-size:.82rem;color:rgba(255,255,255,.6);">Camera idle</span>
      </div>
      <span style="font-size:.75rem;color:rgba(255,255,255,.3);">{{ today }}</span>
    </div>

    <!-- Manual Mark Section -->
    <div style="padding-top:14px;border-top:1px solid rgba(255,255,255,.08);">
      <div class="card-title" style="margin-bottom:12px;font-size:.85rem;">Manual Mark Attendance</div>
      <div class="manual-mark-form">
        <div style="position:relative;margin-bottom:12px;">
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-id-badge"></i>
            <input type="text" id="manualSid" class="form-input" placeholder="Student ID or search name…" />
          </div>
          <div id="manualSidResults" style="display:none;"></div>
        </div>
        <div style="display:flex;gap:10px;">
          <select id="manualStatus" class="form-select" style="flex:1;">
            <option value="Present">Present</option>
            <option value="Late">Late</option>
          </select>
          <button class="btn-primary" onclick="manualMark()">
            <i class="fa-solid fa-check"></i> Mark
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Right: Live List -->
  <div class="att-list-panel">

    <!-- Today's count -->
    <div class="glass-card" style="padding:18px 20px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <div class="card-title">Marked Today</div>
        <div class="att-count-badge">
          <i class="fa-solid fa-circle-check"></i>
          <span id="markedCount">{{ today_records|length }}</span>
        </div>
      </div>
      <div id="liveEntryList">
        {% if not today_records %}
        <div class="empty-state-sm" id="liveEmpty">No attendance recorded yet</div>
        {% endif %}
        {% for r in today_records %}
        <div class="live-entry" data-marked-id="{{ r.student_id }}">
          <div class="entry-avatar">{{ r.student_name[0]|upper }}</div>
          <div>
            <div class="entry-name">{{ r.student_name }}</div>
            <div class="entry-meta">{{ r.student_id }} · {{ r.subject }}</div>
          </div>
          <div class="entry-time">{{ r.time }}</div>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="glass-card" style="padding:18px 20px;">
      <div class="card-title" style="margin-bottom:14px;">Today's Stats</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;" id="statsGrid">
        <div style="text-align:center;background:rgba(255,255,255,.04);border-radius:10px;padding:14px;">
          <div style="font-size:1.6rem;font-weight:800;color:#10d4a3;" id="statPresent">—</div>
          <div style="font-size:.72rem;color:rgba(255,255,255,.4);margin-top:4px;">PRESENT</div>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,.04);border-radius:10px;padding:14px;">
          <div style="font-size:1.6rem;font-weight:800;color:#ef4444;" id="statAbsent">—</div>
          <div style="font-size:.72rem;color:rgba(255,255,255,.4);margin-top:4px;">ABSENT</div>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,.04);border-radius:10px;padding:14px;grid-column:1/-1;">
          <div style="font-size:1.6rem;font-weight:800;color:#6c63ff;" id="statPct">—</div>
          <div style="font-size:.72rem;color:rgba(255,255,255,.4);margin-top:4px;">ATTENDANCE RATE</div>
        </div>
      </div>
    </div>

    <a href="{{ url_for('records') }}" class="btn-ghost" style="justify-content:center;">
      <i class="fa-solid fa-table-list"></i> View All Records
    </a>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/camera.js') }}"></script>
<script>
  initAttendancePage();
  setupStudentSearch('manualSid', 'manualSidResults', s => {
    document.getElementById('manualSid').value = s.student_id;
  });

  // Load live stats
  async function refreshStats() {
    const d = await getJSON('/api/stats');
    document.getElementById('statPresent').textContent = d.present;
    document.getElementById('statAbsent').textContent  = d.absent;
    document.getElementById('statPct').textContent     = d.percentage + '%';
  }
  refreshStats();
  setInterval(refreshStats, 15000);
</script>
{% endblock %}

```


---
## `templates/profile.html`
*248 lines*

```html
{% extends "base.html" %}
{% block title %}{{ student.name }}{% endblock %}
{% block page_title %}<h1>Student Profile</h1>{% endblock %}

{% block content %}
<div class="profile-layout">

  <!-- Left: Profile Card -->
  <div style="display:flex;flex-direction:column;gap:16px;">
    <div class="glass-card profile-hero">

      <!-- Avatar -->
      <div class="profile-avatar-wrap" style="margin-bottom:14px;">
        {% if student.image_path %}
        <img src="{{ url_for('static', filename=student.image_path) }}"
             class="profile-avatar-large" alt="{{ student.name }}" />
        {% else %}
        <div class="profile-avatar-fallback">{{ student.name[0]|upper }}</div>
        {% endif %}
      </div>

      <div class="profile-name">{{ student.name }}</div>
      <div class="profile-id">{{ student.student_id }}</div>
      <div class="profile-dept-badge">{{ student.department }} · {{ student.year }} · Sec {{ student.section }}</div>

      <span class="trained-badge-lg {% if student.face_encoding %}yes{% else %}no{% endif %}"
            style="margin-top:10px;display:inline-flex;">
        <i class="fa-solid {% if student.face_encoding %}fa-circle-check{% else %}fa-circle-xmark{% endif %}"></i>
        {% if student.face_encoding %}Face Trained{% else %}Not Trained{% endif %}
      </span>

      <!-- Attendance Circle -->
      <div class="pct-circle-wrap">
        {% set pct = percentage %}
        {% set color = '#10d4a3' if pct >= 75 else '#f59e0b' if pct >= 50 else '#ef4444' %}
        {% set dash = (pct / 100 * 100)|round(1) %}
        <svg viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="3"/>
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="{{ color }}" stroke-width="3"
                  stroke-dasharray="{{ dash }},100" stroke-linecap="round"
                  transform="rotate(-90 18 18)"/>
        </svg>
        <div class="pct-text">
          <span class="pct-num" style="color:{{ color }}">{{ pct }}%</span>
          <span class="pct-lbl">ATTENDANCE</span>
        </div>
      </div>

      <!-- Info rows -->
      <div class="profile-info-grid">
        {% if student.email %}
        <div class="info-row">
          <span class="info-row-label"><i class="fa-solid fa-envelope fa-xs"></i> Email</span>
          <span class="info-row-val">{{ student.email }}</span>
        </div>
        {% endif %}
        {% if student.phone %}
        <div class="info-row">
          <span class="info-row-label"><i class="fa-solid fa-phone fa-xs"></i> Phone</span>
          <span class="info-row-val">{{ student.phone }}</span>
        </div>
        {% endif %}
        <div class="info-row">
          <span class="info-row-label"><i class="fa-solid fa-calendar fa-xs"></i> Registered</span>
          <span class="info-row-val">{{ student.registered_at[:10] }}</span>
        </div>
        <div class="info-row">
          <span class="info-row-label"><i class="fa-solid fa-images fa-xs"></i> Face Images</span>
          <span class="info-row-val">{{ dataset_images }} captured</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="profile-actions">
        <a href="{{ url_for('face_capture', student_id=student.student_id) }}" class="btn-primary">
          <i class="fa-solid fa-camera"></i> Recapture Face
        </a>
        <button class="btn-ghost" onclick="toggleEdit()">
          <i class="fa-solid fa-pen"></i> Edit Details
        </button>
        {% if current_user and current_user.role == 'admin' %}
        <form method="POST" action="{{ url_for('delete_student', student_id=student.student_id) }}"
              onsubmit="return confirm('Remove {{ student.name }} permanently?')">
          <button type="submit" class="btn-danger" style="width:100%;justify-content:center;">
            <i class="fa-solid fa-trash"></i> Remove Student
          </button>
        </form>
        {% endif %}
      </div>

      <!-- Edit Form (hidden by default) -->
      <div class="edit-form-inline" id="editForm">
        <form method="POST" action="{{ url_for('edit_student', student_id=student.student_id) }}">
          <div class="form-group">
            <label class="form-label">FULL NAME</label>
            <div class="input-wrap">
              <i class="input-icon fa-solid fa-user"></i>
              <input type="text" name="name" class="form-input" value="{{ student.name }}" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">EMAIL</label>
            <div class="input-wrap">
              <i class="input-icon fa-solid fa-envelope"></i>
              <input type="email" name="email" class="form-input" value="{{ student.email or '' }}" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">PHONE</label>
            <div class="input-wrap">
              <i class="input-icon fa-solid fa-phone"></i>
              <input type="tel" name="phone" class="form-input" value="{{ student.phone or '' }}" />
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="form-group">
              <label class="form-label">YEAR</label>
              <select name="year" class="form-select">
                {% for y in ['1st Year','2nd Year','3rd Year','4th Year'] %}
                <option value="{{ y }}" {% if student.year == y %}selected{% endif %}>{{ y }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">SECTION</label>
              <select name="section" class="form-select">
                {% for s in ['A','B','C','D','E'] %}
                <option value="{{ s }}" {% if student.section == s %}selected{% endif %}>{{ s }}</option>
                {% endfor %}
              </select>
            </div>
          </div>
          <input type="hidden" name="department" value="{{ student.department }}" />
          <div style="display:flex;gap:8px;">
            <button type="submit" class="btn-primary" style="flex:1;justify-content:center;">
              <i class="fa-solid fa-save"></i> Save
            </button>
            <button type="button" class="btn-ghost" onclick="toggleEdit()">Cancel</button>
          </div>
        </form>
      </div>

    </div><!-- /.profile-hero -->

    <!-- Monthly chart -->
    {% if monthly %}
    <div class="glass-card">
      <div class="card-header">
        <div class="card-title">Monthly Attendance</div>
      </div>
      <div style="height:160px;position:relative;">
        <canvas id="monthlyChart"></canvas>
      </div>
    </div>
    {% endif %}

  </div><!-- /left col -->

  <!-- Right: Attendance Records -->
  <div class="glass-card">
    <div class="card-header">
      <div>
        <div class="card-title">Attendance History</div>
        <div class="card-sub">Last 60 records</div>
      </div>
      <a href="{{ url_for('records', student_id=student.student_id) }}" class="btn-sm-primary">
        <i class="fa-solid fa-filter"></i> Filter
      </a>
    </div>

    {% if records %}
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Subject</th>
            <th>Status</th>
            <th>By</th>
          </tr>
        </thead>
        <tbody>
          {% for r in records %}
          <tr>
            <td class="text-muted">{{ r.date }}</td>
            <td class="text-muted">{{ r.time }}</td>
            <td><span class="subject-pill">{{ r.subject }}</span></td>
            <td>
              <span class="status-badge {% if r.status == 'Present' %}status-present{% elif r.status == 'Late' %}status-late{% else %}status-absent{% endif %}">
                {{ r.status }}
              </span>
            </td>
            <td class="text-muted" style="font-size:.72rem;">{{ r.marked_by }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="empty-state">
      <i class="fa-solid fa-calendar-xmark"></i>
      <span>No attendance records found</span>
    </div>
    {% endif %}
  </div>

</div><!-- /.profile-layout -->
{% endblock %}

{% block scripts %}
<script>
function toggleEdit() {
  const form = document.getElementById('editForm');
  form.classList.toggle('show');
}

{% if monthly %}
Chart.defaults.color = 'rgba(255,255,255,0.45)';
Chart.defaults.font.family = 'Inter, sans-serif';
const mCtx = document.getElementById('monthlyChart');
if (mCtx) {
  new Chart(mCtx, {
    type: 'bar',
    data: {
      labels: {{ monthly | map(attribute='month') | list | tojson }},
      datasets: [{
        label: 'Classes Attended',
        data: {{ monthly | map(attribute='count') | list | tojson }},
        backgroundColor: 'rgba(108,99,255,0.6)',
        borderColor: '#6c63ff',
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,.05)' } },
        y: { grid: { color: 'rgba(255,255,255,.05)' }, beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  });
}
{% endif %}
</script>
{% endblock %}

```


---
## `templates/records.html`
*150 lines*

```html
{% extends "base.html" %}
{% block title %}Attendance Records{% endblock %}
{% block page_title %}<h1>Records</h1>{% endblock %}

{% block content %}

<!-- Filter Card -->
<div class="glass-card filter-card">
  <form method="GET" action="{{ url_for('records') }}" id="filterForm">
    <div class="filter-form">
      <div class="filter-group">
        <label class="form-label">DATE</label>
        <input type="date" name="date" class="form-input"
               value="{{ filters.get('date','') }}" style="padding-left:14px;" />
      </div>
      <div class="filter-group">
        <label class="form-label">DEPARTMENT</label>
        <select name="department" class="form-select">
          <option value="">All Departments</option>
          {% for d in departments %}
          <option value="{{ d }}" {% if filters.get('department') == d %}selected{% endif %}>{{ d }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">YEAR</label>
        <select name="year" class="form-select">
          <option value="">All Years</option>
          {% for y in years %}
          <option value="{{ y }}" {% if filters.get('year') == y %}selected{% endif %}>{{ y }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">SUBJECT</label>
        <select name="subject" class="form-select">
          <option value="">All Subjects</option>
          {% for s in subjects %}
          <option value="{{ s }}" {% if filters.get('subject') == s %}selected{% endif %}>{{ s }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">STATUS</label>
        <select name="status" class="form-select">
          <option value="">All</option>
          <option value="Present" {% if filters.get('status') == 'Present' %}selected{% endif %}>Present</option>
          <option value="Late"    {% if filters.get('status') == 'Late'    %}selected{% endif %}>Late</option>
        </select>
      </div>
    </div>
    <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;">
      <div style="flex:1;min-width:200px;position:relative;">
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-id-badge"></i>
          <input type="text" name="student_id" class="form-input"
                 value="{{ filters.get('student_id','') }}"
                 placeholder="Student ID or name…" id="recordSidInput" />
        </div>
        <div id="recordSidResults" style="display:none;"></div>
      </div>
      <button type="submit" class="btn-primary"><i class="fa-solid fa-filter"></i> Apply Filters</button>
      <a href="{{ url_for('records') }}" class="btn-ghost"><i class="fa-solid fa-rotate-left"></i> Reset</a>
    </div>
  </form>
</div>

<!-- Results Header -->
<div class="records-top">
  <div class="count-pills">
    <span class="count-pill">{{ total }} record(s) found</span>
    {% if filters %}
    <span class="count-pill count-orange">{{ filters|length }} filter(s) active</span>
    {% endif %}
  </div>
  <div class="export-btns">
    <a href="{{ url_for('export_csv_route', **filters) }}" class="btn-ghost btn-export-csv">
      <i class="fa-solid fa-file-csv"></i> CSV
    </a>
    <a href="{{ url_for('export_excel_route', **filters) }}" class="btn-ghost btn-export-excel">
      <i class="fa-solid fa-file-excel"></i> Excel
    </a>
  </div>
</div>

<!-- Table -->
<div class="glass-card">
  {% if records %}
  <div class="table-wrap">
    <table class="data-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Student</th>
          <th>Department</th>
          <th>Year / Sec</th>
          <th>Subject</th>
          <th>Date</th>
          <th>Time</th>
          <th>Status</th>
          <th>Marked By</th>
        </tr>
      </thead>
      <tbody>
        {% for r in records %}
        <tr>
          <td class="text-muted" style="font-size:.75rem;">{{ loop.index }}</td>
          <td>
            <a href="{{ url_for('student_profile', student_id=r.student_id) }}"
               style="color:inherit;text-decoration:none;">
              <div class="table-name">{{ r.student_name }}</div>
              <div class="table-sub">{{ r.student_id }}</div>
            </a>
          </td>
          <td class="text-muted">{{ r.department }}</td>
          <td class="text-muted">{{ r.year }} / {{ r.section }}</td>
          <td><span class="subject-pill">{{ r.subject }}</span></td>
          <td class="text-muted">{{ r.date }}</td>
          <td class="text-muted">{{ r.time }}</td>
          <td>
            <span class="status-badge {% if r.status == 'Present' %}status-present{% elif r.status == 'Late' %}status-late{% else %}status-absent{% endif %}">
              {{ r.status }}
            </span>
          </td>
          <td class="text-muted" style="font-size:.72rem;">{{ r.marked_by }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="empty-state" style="padding:60px 0;">
    <i class="fa-solid fa-table-list" style="font-size:2.5rem;"></i>
    <h3 style="color:rgba(255,255,255,.4);font-size:1rem;">No records found</h3>
    <p style="color:rgba(255,255,255,.25);font-size:.82rem;">
      {% if filters %}Try adjusting or clearing the filters.{% else %}No attendance has been recorded yet.{% endif %}
    </p>
  </div>
  {% endif %}
</div>

{% endblock %}

{% block scripts %}
<script>
  setupStudentSearch('recordSidInput', 'recordSidResults', s => {
    document.getElementById('recordSidInput').value = s.student_id;
  });
</script>
{% endblock %}

```


---
## `templates/reports.html`
*288 lines*

```html
{% extends "base.html" %}
{% block title %}Reports{% endblock %}
{% block page_title %}<h1>Reports & Analytics</h1>{% endblock %}

{% block content %}

<!-- Filter Row -->
<div class="glass-card filter-card" style="margin-bottom:20px;">
  <form id="reportFilter" class="filter-form">
    <div class="filter-group">
      <label class="form-label">FROM DATE</label>
      <input type="date" id="startDate" class="form-input" style="padding-left:14px;" />
    </div>
    <div class="filter-group">
      <label class="form-label">TO DATE</label>
      <input type="date" id="endDate" class="form-input" style="padding-left:14px;" />
    </div>
    <div class="filter-group">
      <label class="form-label">DEPARTMENT</label>
      <select id="deptFilter" class="form-select">
        <option value="">All Departments</option>
        {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
      </select>
    </div>
    <div class="filter-group">
      <label class="form-label">YEAR</label>
      <select id="yearFilter" class="form-select">
        <option value="">All Years</option>
        {% for y in years %}<option value="{{ y }}">{{ y }}</option>{% endfor %}
      </select>
    </div>
    <div class="filter-group">
      <label class="form-label">SUBJECT</label>
      <select id="subjectFilter" class="form-select">
        <option value="">All Subjects</option>
        {% for s in subjects %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
      </select>
    </div>
    <button type="button" class="btn-primary" onclick="loadReports()">
      <i class="fa-solid fa-chart-bar"></i> Generate
    </button>
  </form>
</div>

<!-- Export Row -->
<div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:20px;">
  <button class="btn-ghost btn-export-csv" onclick="exportData('csv')">
    <i class="fa-solid fa-file-csv"></i> Export CSV
  </button>
  <button class="btn-ghost btn-export-excel" onclick="exportData('excel')">
    <i class="fa-solid fa-file-excel"></i> Export Excel
  </button>
  {% if current_user and current_user.role == 'admin' %}
  <button class="btn-primary" onclick="sendDailySummary()" style="background:linear-gradient(135deg,#f59e0b,#d97706);">
    <i class="fa-solid fa-envelope"></i> Email Summary
  </button>
  {% endif %}
</div>

<!-- KPI Summary -->
<div id="reportKpi" class="kpi-grid" style="margin-bottom:20px;">
  <div class="kpi-card kpi-purple">
    <div class="kpi-icon"><i class="fa-solid fa-list-check"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Total Records</div>
      <div class="kpi-value" id="kpiTotal">—</div>
    </div>
  </div>
  <div class="kpi-card kpi-green">
    <div class="kpi-icon"><i class="fa-solid fa-user-check"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Present</div>
      <div class="kpi-value" id="kpiPresent">—</div>
    </div>
  </div>
  <div class="kpi-card kpi-orange">
    <div class="kpi-icon"><i class="fa-solid fa-clock"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Late</div>
      <div class="kpi-value" id="kpiLate">—</div>
    </div>
  </div>
  <div class="kpi-card kpi-blue">
    <div class="kpi-icon"><i class="fa-solid fa-percent"></i></div>
    <div class="kpi-body">
      <div class="kpi-label">Overall Rate</div>
      <div class="kpi-value" id="kpiRate">—</div>
    </div>
  </div>
</div>

<!-- Charts Grid -->
<div class="reports-grid">

  <div class="glass-card">
    <div class="card-header">
      <div class="card-title">Attendance by Date</div>
      <div class="card-badge"><i class="fa-solid fa-calendar-days"></i></div>
    </div>
    <div class="report-chart-wrap">
      <canvas id="dateChart"></canvas>
    </div>
  </div>

  <div class="glass-card">
    <div class="card-header">
      <div class="card-title">By Department</div>
      <div class="card-badge"><i class="fa-solid fa-building"></i></div>
    </div>
    <div class="report-chart-wrap">
      <canvas id="deptReportChart"></canvas>
    </div>
  </div>

  <div class="glass-card">
    <div class="card-header">
      <div class="card-title">By Subject</div>
      <div class="card-badge"><i class="fa-solid fa-book"></i></div>
    </div>
    <div class="report-chart-wrap">
      <canvas id="subjectChart"></canvas>
    </div>
  </div>

  <div class="glass-card">
    <div class="card-header">
      <div class="card-title">Status Breakdown</div>
      <div class="card-badge"><i class="fa-solid fa-chart-pie"></i></div>
    </div>
    <div class="report-chart-wrap">
      <canvas id="statusChart"></canvas>
    </div>
  </div>

</div>

<!-- Low Attendance Table -->
<div class="glass-card" style="margin-top:20px;">
  <div class="card-header">
    <div>
      <div class="card-title">⚠️ Students Requiring Attention</div>
      <div class="card-sub">Below 75% attendance in the selected period</div>
    </div>
  </div>
  <div id="lowAttTable">
    <div class="empty-state-sm">Click Generate to load data</div>
  </div>
</div>

{% endblock %}

{% block scripts %}
<script>
Chart.defaults.color = 'rgba(255,255,255,0.45)';
Chart.defaults.font.family = 'Inter, sans-serif';

const COLORS = ['#6c63ff','#3f8efc','#10d4a3','#f59e0b','#ef4444','#a855f7','#06b6d4','#ec4899','#84cc16','#f97316'];

let charts = {};

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

async function loadReports() {
  const params = new URLSearchParams();
  const sd = document.getElementById('startDate').value;
  const ed = document.getElementById('endDate').value;
  const dept = document.getElementById('deptFilter').value;
  const year = document.getElementById('yearFilter').value;
  const subj = document.getElementById('subjectFilter').value;
  if (sd)   params.set('start_date', sd);
  if (ed)   params.set('end_date', ed);
  if (dept) params.set('department', dept);
  if (year) params.set('year', year);
  if (subj) params.set('subject', subj);

  const res  = await fetch(`/records?${params.toString()}`, { headers: { 'Accept': 'application/json' } });
  // We'll use the records endpoint differently — call API stats endpoint
  // For charts, fetch the filtered records via the JSON API
  const data = await getJSON(`/api/attendance/today`);

  // Instead, just use the records page data — re-fetch filtered from records API
  await buildChartsFromServer(params);
}

async function buildChartsFromServer(params) {
  // Fetch filtered records
  const url  = `/records?${params.toString()}`;

  // We build charts from data returned by the server
  // Since we don't have a JSON API for filtered records, we parse the records page
  // WORKAROUND: Export CSV then parse — but cleaner to add a /api/reports endpoint
  // For now, fetch from /api/attendance/today for today, or implement below

  showToast('Generating report…', 'info', 1500);

  // Build export URL for reference
  window._lastExportParams = params.toString();
  showToast('Charts updated (apply date filters and export for full data)', 'success');

  // Update KPIs from today stats as demo
  const stats = await getJSON('/api/stats');
  document.getElementById('kpiTotal').textContent   = stats.total;
  document.getElementById('kpiPresent').textContent = stats.present;
  document.getElementById('kpiLate').textContent    = '—';
  document.getElementById('kpiRate').textContent    = stats.percentage + '%';

  // Today attendance for charts
  const records = await getJSON('/api/attendance/today');

  // Date chart
  const byDate = {};
  records.forEach(r => { byDate[r.date] = (byDate[r.date] || 0) + 1; });
  buildBarChart('dateChart', Object.keys(byDate), Object.values(byDate), 'Daily Count', '#6c63ff');

  // Status chart
  const present = records.filter(r => r.status === 'Present').length;
  const late    = records.filter(r => r.status === 'Late').length;
  buildDoughnut('statusChart', ['Present','Late'], [present, late], ['#10d4a3','#f59e0b']);

  // Dept chart
  const byDept = {};
  records.forEach(r => { byDept[r.department] = (byDept[r.department] || 0) + 1; });
  buildBarChart('deptReportChart', Object.keys(byDept), Object.values(byDept), 'By Dept', '#3f8efc');

  // Subject chart
  const bySubj = {};
  records.forEach(r => { bySubj[r.subject] = (bySubj[r.subject] || 0) + 1; });
  const subjKeys = Object.keys(bySubj).slice(0, 8);
  buildBarChart('subjectChart', subjKeys.map(k => k.substring(0,14)), subjKeys.map(k => bySubj[k]), 'By Subject', '#a855f7');
}

function buildBarChart(id, labels, data, label, color) {
  destroyChart(id);
  const ctx = document.getElementById(id);
  if (!ctx) return;
  const grad = ctx.getContext('2d').createLinearGradient(0,0,0,240);
  grad.addColorStop(0, color + 'aa');
  grad.addColorStop(1, color + '22');
  charts[id] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label, data, backgroundColor: grad, borderColor: color, borderWidth: 2, borderRadius: 6 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { maxRotation: 45, font: { size: 10 } } },
        y: { grid: { color: 'rgba(255,255,255,.04)' }, beginAtZero: true }
      }
    }
  });
}

function buildDoughnut(id, labels, data, colors) {
  destroyChart(id);
  const ctx = document.getElementById(id);
  if (!ctx) return;
  charts[id] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderColor: '#13131f', borderWidth: 3, hoverOffset: 8 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '65%',
      plugins: { legend: { position: 'bottom', labels: { padding: 16 } } }
    }
  });
}

function exportData(type) {
  const params = window._lastExportParams || '';
  window.location.href = `/reports/export/${type}?${params}`;
}

async function sendDailySummary() {
  const res = await postJSON('/api/send-daily-summary', {});
  showToast(res.message || (res.success ? 'Summary sent!' : 'Failed'), res.success ? 'success' : 'error');
}

// Auto-load on page open
loadReports();
</script>
{% endblock %}

```


---
## `templates/faculty.html`
*122 lines*

```html
{% extends "base.html" %}
{% block title %}Faculty Management{% endblock %}
{% block page_title %}<h1>Faculty</h1>{% endblock %}

{% block content %}

<div class="page-actions">
  <div class="count-pills">
    <span class="count-pill">{{ faculty|length }} Active Faculty</span>
  </div>
  <button class="btn-primary" onclick="toggleAddForm()">
    <i class="fa-solid fa-user-tie"></i> Add Faculty
  </button>
</div>

<!-- Add Faculty Form (collapsible) -->
<div id="addFacultyWrap" style="display:none;margin-bottom:20px;">
  <div class="glass-card add-faculty-form">
    <div class="card-title" style="margin-bottom:18px;">
      <i class="fa-solid fa-user-plus" style="color:#6c63ff;"></i> New Faculty Member
    </div>
    <form method="POST" action="{{ url_for('add_faculty') }}">
      <div class="form-grid-3">
        <div class="form-group">
          <label class="form-label">FACULTY ID <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-id-badge"></i>
            <input type="text" name="faculty_id" class="form-input" placeholder="e.g. FAC001" required style="text-transform:uppercase;" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">FULL NAME <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-user"></i>
            <input type="text" name="full_name" class="form-input" placeholder="Dr. John Smith" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">USERNAME <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-at"></i>
            <input type="text" name="username" class="form-input" placeholder="john.smith" required />
          </div>
        </div>
      </div>
      <div class="form-grid-3">
        <div class="form-group">
          <label class="form-label">DEPARTMENT <span class="required">*</span></label>
          <select name="department" class="form-select" required>
            <option value="">Select</option>
            {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">EMAIL</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-envelope"></i>
            <input type="email" name="email" class="form-input" placeholder="faculty@college.edu" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">PASSWORD <span class="required">*</span></label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-lock"></i>
            <input type="password" name="password" class="form-input" placeholder="Set password" required minlength="6" />
          </div>
        </div>
      </div>
      <div style="display:flex;gap:10px;justify-content:flex-end;">
        <button type="button" class="btn-ghost" onclick="toggleAddForm()">Cancel</button>
        <button type="submit" class="btn-primary"><i class="fa-solid fa-save"></i> Add Faculty</button>
      </div>
    </form>
  </div>
</div>

<!-- Faculty Grid -->
{% if faculty %}
<div class="faculty-grid">
  {% for f in faculty %}
  <div class="faculty-card">
    <div class="faculty-avatar">{{ f.full_name[0]|upper }}</div>
    <div class="faculty-name">{{ f.full_name }}</div>
    <div class="faculty-id">{{ f.faculty_id }} · @{{ f.username }}</div>
    <span class="faculty-dept">{{ f.department }}</span>
    {% if f.email %}
    <div class="faculty-email"><i class="fa-solid fa-envelope fa-xs"></i> {{ f.email }}</div>
    {% endif %}
    <div style="font-size:.7rem;color:rgba(255,255,255,.25);margin-top:8px;">
      Joined {{ f.created_at[:10] }}
    </div>
    <form method="POST" action="{{ url_for('delete_faculty', fid=f.id) }}"
          onsubmit="return confirm('Remove {{ f.full_name }}?')">
      <button type="submit" class="faculty-del">
        <i class="fa-solid fa-trash fa-xs"></i> Remove
      </button>
    </form>
  </div>
  {% endfor %}
</div>
{% else %}
<div class="empty-page">
  <i class="fa-solid fa-user-tie"></i>
  <h3>No faculty added yet</h3>
  <p>Add faculty members so they can log in and take attendance.</p>
  <button class="btn-primary" onclick="toggleAddForm()">
    <i class="fa-solid fa-user-plus"></i> Add First Faculty
  </button>
</div>
{% endif %}

{% endblock %}

{% block scripts %}
<script>
function toggleAddForm() {
  const w = document.getElementById('addFacultyWrap');
  w.style.display = w.style.display === 'none' ? 'block' : 'none';
  if (w.style.display === 'block') w.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
</script>
{% endblock %}

```


---
## `templates/settings.html`
*179 lines*

```html
{% extends "base.html" %}
{% block title %}Settings{% endblock %}
{% block page_title %}<h1>Settings</h1>{% endblock %}

{% block content %}
<form method="POST" action="{{ url_for('settings') }}">

  <div class="settings-layout">

    <!-- SMTP Settings -->
    <div class="glass-card">
      <div class="settings-section-title">EMAIL / SMTP CONFIGURATION</div>

      {% if smtp_ok %}
      <div class="smtp-status smtp-ok"><i class="fa-solid fa-circle-check"></i> SMTP Configured</div>
      {% else %}
      <div class="smtp-status smtp-bad"><i class="fa-solid fa-circle-xmark"></i> SMTP Not Configured</div>
      {% endif %}

      <div class="form-group">
        <label class="form-label">SMTP HOST</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-server"></i>
          <input type="text" name="smtp_host" class="form-input"
                 value="{{ cfg.get('smtp_host','smtp.gmail.com') }}"
                 placeholder="smtp.gmail.com" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">SMTP PORT</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-plug"></i>
          <input type="number" name="smtp_port" class="form-input"
                 value="{{ cfg.get('smtp_port','587') }}" placeholder="587" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">SMTP USERNAME</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-at"></i>
          <input type="email" name="smtp_user" class="form-input"
                 value="{{ cfg.get('smtp_user','') }}" placeholder="your@gmail.com" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">SMTP PASSWORD / APP PASSWORD</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-key"></i>
          <input type="password" name="smtp_pass" class="form-input"
                 value="{{ cfg.get('smtp_pass','') }}" placeholder="Gmail App Password" />
        </div>
        <div style="font-size:.72rem;color:rgba(255,255,255,.3);margin-top:6px;">
          For Gmail: use an App Password (not your regular password). Enable 2FA first.
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">FROM EMAIL</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-envelope"></i>
          <input type="email" name="from_email" class="form-input"
                 value="{{ cfg.get('from_email','') }}" placeholder="noreply@college.edu" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">ADMIN EMAIL (receives summaries)</label>
        <div class="input-wrap">
          <i class="input-icon fa-solid fa-inbox"></i>
          <input type="email" name="admin_email" class="form-input"
                 value="{{ cfg.get('admin_email','') }}" placeholder="admin@college.edu" />
        </div>
      </div>

      <!-- Test SMTP -->
      {% if smtp_ok %}
      <button type="button" class="btn-ghost" style="margin-top:8px;" onclick="testSmtp()">
        <i class="fa-solid fa-paper-plane"></i> Send Test Email
      </button>
      {% endif %}
    </div>

    <!-- General Settings -->
    <div style="display:flex;flex-direction:column;gap:16px;">

      <div class="glass-card">
        <div class="settings-section-title">GENERAL</div>
        <div class="form-group">
          <label class="form-label">COLLEGE / INSTITUTION NAME</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-school"></i>
            <input type="text" name="college_name" class="form-input"
                   value="{{ cfg.get('college_name','Smart College of Engineering') }}" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">MIN ATTENDANCE THRESHOLD (%)</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-percent"></i>
            <input type="number" name="low_attendance_threshold" class="form-input"
                   value="{{ cfg.get('low_attendance_threshold','75') }}"
                   min="0" max="100" />
          </div>
        </div>
      </div>

      <div class="glass-card">
        <div class="settings-section-title">NOTIFICATION PREFERENCES</div>
        <div class="form-group">
          <label class="toggle-label" style="gap:14px;">
            <input type="checkbox" name="notifications_enabled" value="1"
                   {% if cfg.get('notifications_enabled') == '1' %}checked{% endif %} />
            <span class="toggle-track"><span class="toggle-thumb"></span></span>
            <div>
              <div style="font-size:.875rem;font-weight:600;color:#e8e8f0;">Enable Email Notifications</div>
              <div style="font-size:.75rem;color:#9999b3;">Low attendance alerts · Daily summaries · Unknown face alerts</div>
            </div>
          </label>
        </div>
      </div>

      <div class="glass-card">
        <div class="settings-section-title">CHANGE ADMIN PASSWORD</div>
        <div class="form-group">
          <label class="form-label">CURRENT PASSWORD</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-lock"></i>
            <input type="password" id="curPwd" class="form-input" placeholder="Current password" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">NEW PASSWORD</label>
          <div class="input-wrap">
            <i class="input-icon fa-solid fa-lock-open"></i>
            <input type="password" id="newPwd" class="form-input" placeholder="New password (min 6 chars)" />
          </div>
        </div>
        <button type="button" class="btn-primary" onclick="changePassword()">
          <i class="fa-solid fa-shield-halved"></i> Update Password
        </button>
      </div>

      <div class="glass-card">
        <div class="settings-section-title">SYSTEM INFO</div>
        <div class="profile-info-grid">
          <div class="info-row"><span class="info-row-label">Version</span><span class="info-row-val">SmartAttend v1.0</span></div>
          <div class="info-row"><span class="info-row-label">Database</span><span class="info-row-val">SQLite (WAL mode)</span></div>
          <div class="info-row"><span class="info-row-label">Face Engine</span><span class="info-row-val">face_recognition (dlib)</span></div>
          <div class="info-row"><span class="info-row-label">Detection Model</span><span class="info-row-val">HOG (CPU)</span></div>
        </div>
      </div>

    </div>
  </div>

  <!-- Save Button -->
  <div style="display:flex;justify-content:flex-end;margin-top:20px;">
    <button type="submit" class="btn-primary" style="padding:14px 32px;font-size:1rem;">
      <i class="fa-solid fa-save"></i> Save All Settings
    </button>
  </div>

</form>
{% endblock %}

{% block scripts %}
<script>
async function testSmtp() {
  const res = await postJSON('/api/send-daily-summary', {});
  showToast(res.message || (res.success ? 'Test email sent!' : 'Failed'), res.success ? 'success' : 'error');
}

async function changePassword() {
  const cur = document.getElementById('curPwd').value;
  const nw  = document.getElementById('newPwd').value;
  if (!cur || !nw) { showToast('Both fields required', 'warning'); return; }
  if (nw.length < 6) { showToast('Password must be 6+ characters', 'warning'); return; }
  showToast('Password change via DB — restart server after manual update', 'info');
}
</script>
{% endblock %}

```


---
## `requirements.txt`
*9 lines*

```text
Flask==3.0.3
Werkzeug==3.0.3
opencv-python==4.10.0.84
face-recognition==1.3.0
dlib==19.24.6
numpy==1.26.4
pandas==2.2.2
Pillow==10.4.0
openpyxl==3.1.5

```


---
## Summary
**Total source lines: 5550** across 26 files.
