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
        cols = [c for c in COLUMNS if c in df.columns]
        return df[cols]
    return pd.DataFrame(columns=COLUMNS)


def export_csv(filters: dict = None) -> bytes:
    """Generate CSV byte string for download."""
    return _build_df(filters).to_csv(index=False).encode('utf-8')


def export_excel(filters: dict = None) -> bytes:
    """Generate stylized Excel workbook byte string."""
    df     = _build_df(filters)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
        ws = writer.sheets['Attendance']
        for col_cells in ws.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 40)
    output.seek(0)
    return output.getvalue()
