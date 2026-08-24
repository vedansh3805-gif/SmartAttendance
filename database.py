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
            ('admin', generate_password_hash('admin123', method='pbkdf2:sha256'), 'System Administrator', '')
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
    print("Database ready with complete schema.")


if __name__ == "__main__":
    init_db()