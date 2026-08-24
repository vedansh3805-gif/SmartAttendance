from datetime import datetime, date, timedelta
from database import get_db
from config import Config


def mark_attendance(student_id: str, subject: str, status: str = 'Present', marked_by: str = 'AI'):
    """
    Mark attendance for one student in one subject today.
    Prevents duplicate entries (one per student per subject per day).
    Returns (success: bool, message: str).
    """
    today = date.today().isoformat()
    now   = datetime.now().strftime('%H:%M:%S')

    db = get_db()

    # Duplicate check for the day and subject
    dup = db.execute(
        "SELECT id, time FROM attendance WHERE student_id=? AND date=? AND subject=?",
        (student_id, today, subject)
    ).fetchone()
    if dup:
        db.close()
        return False, f"Already marked for {subject} today at {dup['time']}"

    # Fetch student details
    student = db.execute(
        "SELECT * FROM students WHERE student_id=? AND is_active=1", (student_id,)
    ).fetchone()
    if not student:
        db.close()
        return False, "Student not found or inactive"

    db.execute(
        '''INSERT INTO attendance
           (student_id, student_name, department, year, section, date, time, subject, status, marked_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (student_id, student['name'], student['department'], student['year'],
         student['section'], today, now, subject, status, marked_by)
    )
    db.commit()
    db.close()
    return True, f"✓ {student['name']} ({student_id}) marked {status}"


def get_today_stats():
    """Returns today's total, present, absent count and attendance %."""
    today = date.today().isoformat()
    db    = get_db()
    total = db.execute("SELECT COUNT(*) FROM students WHERE is_active=1").fetchone()[0]
    present = db.execute(
        "SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=?", (today,)
    ).fetchone()[0]
    db.close()
    absent  = max(0, total - present)
    pct     = round(present / total * 100, 1) if total > 0 else 0
    return {'total': total, 'present': present, 'absent': absent, 'percentage': pct}


def get_student_attendance_percentage(student_id: str) -> float:
    """Calculate overall attendance percentage for a single student."""
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


def get_low_attendance_students(threshold: float = None):
    """Retrieve students whose attendance percentage is below threshold."""
    if threshold is None:
        threshold = Config.MIN_ATTENDANCE_PCT

    db       = get_db()
    students = db.execute(
        "SELECT student_id, name, department, year, section, email FROM students WHERE is_active=1"
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
                'email':      s['email'],
                'percentage': pct,
            })
    return sorted(result, key=lambda x: x['percentage'])


def get_weekly_trend():
    """Last 7 days daily distinct student counts: [{date, count}]"""
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
    """Attendance count grouped by department for a given date."""
    for_date = for_date or date.today().isoformat()
    db = get_db()
    rows = db.execute(
        '''SELECT department, COUNT(DISTINCT student_id) AS present
           FROM attendance WHERE date=?
           GROUP BY department ORDER BY department''',
        (for_date,)
    ).fetchall()

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
