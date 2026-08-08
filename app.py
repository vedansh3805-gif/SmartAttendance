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
    app.run(debug=True, host='0.0.0.0', port=5001)
