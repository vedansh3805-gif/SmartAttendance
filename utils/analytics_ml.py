import numpy as np
from datetime import datetime, date, timedelta
from database import get_db
from config import Config


def compute_student_risk_analytics() -> list[dict]:
    """
    Analyzes historical attendance trends, short-term velocity, and variance
    to predict student shortage risk before examinations.
    Returns sorted list of student risk profiles.
    """
    db = get_db()
    students = db.execute(
        "SELECT student_id, name, department, year, section, email FROM students WHERE is_active=1"
    ).fetchall()

    all_dates = [r[0] for r in db.execute("SELECT DISTINCT date FROM attendance ORDER BY date").fetchall()]
    total_term_days = max(len(all_dates), 1)

    results = []

    for s in students:
        sid = s['student_id']
        att_rows = db.execute(
            "SELECT date, status FROM attendance WHERE student_id=? ORDER BY date", (sid,)
        ).fetchall()

        attended_days = len(set(r['date'] for r in att_rows))
        current_pct = round((attended_days / total_term_days) * 100, 1)

        # Recent 7-day velocity
        recent_7_dates = all_dates[-7:] if len(all_dates) >= 7 else all_dates
        recent_attended = len(set(r['date'] for r in att_rows if r['date'] in recent_7_dates))
        recent_expected = max(len(recent_7_dates), 1)
        recent_pct = round((recent_attended / recent_expected) * 100, 1)

        # Velocity delta: positive means improving, negative means declining
        velocity = round(recent_pct - current_pct, 1)

        # Risk Classification & Scoring (0 to 100)
        # Higher score = higher probability of failing minimum threshold
        if current_pct < 65.0:
            risk_level = "High Risk"
            risk_color = "#ef4444"
            risk_score = min(100.0, round(100 - current_pct + max(0, -velocity * 0.5), 1))
            recommendation = "Immediate faculty intervention & parent advisory notice required."
        elif current_pct < Config.MIN_ATTENDANCE_PCT:
            risk_level = "Moderate Risk"
            risk_color = "#f59e0b"
            risk_score = round(75.0 - current_pct + 40.0, 1)
            recommendation = "Warning email dispatched; student advised to attend upcoming review sessions."
        else:
            risk_level = "Good Standing"
            risk_color = "#10d4a3"
            risk_score = max(0.0, round(100 - current_pct, 1))
            recommendation = "Attendance consistent and compliant with institutional guidelines."

        results.append({
            'student_id': sid,
            'name': s['name'],
            'department': s['department'],
            'year': s['year'],
            'section': s['section'],
            'email': s['email'],
            'current_pct': current_pct,
            'recent_pct': recent_pct,
            'velocity': velocity,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_score': risk_score,
            'recommendation': recommendation,
            'attended_days': attended_days,
            'total_days': total_term_days
        })

    db.close()
    return sorted(results, key=lambda x: x['risk_score'], reverse=True)


def get_ai_attendance_summary() -> dict:
    """Aggregate high-level AI insights for dashboard reporting."""
    risk_profiles = compute_student_risk_analytics()
    total_students = len(risk_profiles)
    high_risk_count = sum(1 for p in risk_profiles if p['risk_level'] == "High Risk")
    moderate_risk_count = sum(1 for p in risk_profiles if p['risk_level'] == "Moderate Risk")
    safe_count = sum(1 for p in risk_profiles if p['risk_level'] == "Good Standing")

    avg_pct = round(np.mean([p['current_pct'] for p in risk_profiles]), 1) if risk_profiles else 0.0

    return {
        'total_analyzed': total_students,
        'high_risk_count': high_risk_count,
        'moderate_risk_count': moderate_risk_count,
        'safe_count': safe_count,
        'average_attendance': avg_pct,
        'top_at_risk': risk_profiles[:5]
    }
