"""SQLite connection and schema.

On a free host the disk is reset on every deploy or restart, so the seed data
comes back and new bookings are lost (see slide 33). Fine for a demo.
"""
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS desks (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE,
    zone  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  TEXT    NOT NULL,
    desk_id     INTEGER NOT NULL REFERENCES desks(id),
    start_time  TEXT    NOT NULL,
    end_time    TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'booked'
                CHECK (status IN ('booked', 'checked_in', 'cancelled'))
);
"""

SEED_DESKS = [
    (1, "A-01", "Quiet zone"),
    (2, "A-02", "Quiet zone"),
    (3, "B-01", "Group zone"),
    (4, "B-02", "Group zone"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT OR IGNORE INTO desks (id, name, zone) VALUES (?, ?, ?)", SEED_DESKS
    )
    conn.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
