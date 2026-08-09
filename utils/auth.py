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
