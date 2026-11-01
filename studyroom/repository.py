"""Data access only: SQL lives here and nowhere else."""
from .db import get_db


def list_desks():
    rows = get_db().execute("SELECT id, name, zone FROM desks ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def desk_exists(desk_id):
    row = get_db().execute("SELECT 1 FROM desks WHERE id = ?", (desk_id,)).fetchone()
    return row is not None


def find_active_booking(student_id, now_iso):
    row = get_db().execute(
        "SELECT * FROM bookings WHERE student_id = ? AND status != 'cancelled'"
        " AND end_time > ?",
        (student_id, now_iso),
    ).fetchone()
    return dict(row) if row else None


def desk_is_taken(desk_id, start_iso, end_iso):
    row = get_db().execute(
        "SELECT 1 FROM bookings WHERE desk_id = ? AND status != 'cancelled'"
        " AND start_time < ? AND end_time > ?",
        (desk_id, end_iso, start_iso),
    ).fetchone()
    return row is not None


def insert_booking(student_id, desk_id, start_iso, end_iso):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO bookings (student_id, desk_id, start_time, end_time)"
        " VALUES (?, ?, ?, ?)",
        (student_id, desk_id, start_iso, end_iso),
    )
    conn.commit()
    return get_booking(cur.lastrowid)


def get_booking(booking_id):
    row = get_db().execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    return dict(row) if row else None


def set_status(booking_id, status):
    conn = get_db()
    conn.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    conn.commit()
    return get_booking(booking_id)
