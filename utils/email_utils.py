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

        return True, "Email sent successfully"
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
        <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:16px;text-align:center;">
          <p style="color:#9999b3;font-size:12px;margin:0 0 8px;">Total Students</p>
          <p style="color:#e8e8f0;font-size:28px;font-weight:700;margin:0;">{stats['total']}</p>
        </div>
        <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:16px;text-align:center;">
          <p style="color:#9999b3;font-size:12px;margin:0 0 8px;">Present Today</p>
          <p style="color:#10d4a3;font-size:28px;font-weight:700;margin:0;">{stats['present']}</p>
        </div>
        <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:16px;text-align:center;">
          <p style="color:#9999b3;font-size:12px;margin:0 0 8px;">Absent Today</p>
          <p style="color:#ef4444;font-size:28px;font-weight:700;margin:0;">{stats['absent']}</p>
        </div>
        <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:16px;text-align:center;">
          <p style="color:#9999b3;font-size:12px;margin:0 0 8px;">Attendance Rate</p>
          <p style="color:{color};font-size:28px;font-weight:700;margin:0;">{pct}%</p>
        </div>
      </div>
      <p style="color:#9999b3;font-size:12px;margin:0;">Auto-generated by SmartAttend.</p>
    </div>
  </div>
</div>
"""
    return send_email(admin_email, subj, plain, html)


def send_unknown_face_alert(admin_email: str):
    today = date.today().strftime('%d %B %Y')
    subj  = "🚨 Security Alert: Unknown Face Detected"
    plain = f"An unrecognised face was detected by the SmartAttend biometric scanner on {today}. Please check the live logs."
    return send_email(admin_email, subj, plain)
