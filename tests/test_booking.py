"""POST /api/bookings — one test per rule, both sides of every boundary."""


def book(client, start, end, student_id="11225678", desk_id=1):
    return client.post("/api/bookings", json={
        "student_id": student_id,
        "desk_id": desk_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
    })


# --- Rule: a booking lasts at most 3 hours -------------------------------

def test_booking_exactly_3_hours_is_allowed(client, at):
    r = book(client, at(9), at(12))
    assert r.status_code == 201


def test_booking_3h30_is_rejected(client, at):
    r = book(client, at(9), at(12, 30))
    assert r.status_code == 422
    assert r.get_json()["error"] == "TOO_LONG"


def test_booking_3h01_is_rejected(client, at):
    r = book(client, at(9), at(12, 1))
    assert r.status_code == 422


# --- Rule: open from 07:00 to 22:00 -------------------------------------

def test_booking_from_7_00_is_allowed(client, at):
    assert book(client, at(7), at(9)).status_code == 201


def test_booking_before_7_00_is_rejected(client, at):
    r = book(client, at(6, 30), at(8))
    assert r.status_code == 422
    assert r.get_json()["error"] == "OUTSIDE_OPENING_HOURS"


def test_booking_until_22_00_is_allowed(client, at):
    assert book(client, at(20), at(22)).status_code == 201


def test_booking_after_22_00_is_rejected(client, at):
    r = book(client, at(20), at(22, 30))
    assert r.status_code == 422


# --- Rule: one active booking per student -------------------------------

def test_second_active_booking_is_rejected(client, at):
    assert book(client, at(9), at(10), desk_id=1).status_code == 201
    r = book(client, at(14), at(15), desk_id=2)
    assert r.status_code == 409
    assert r.get_json()["error"] == "ALREADY_HAS_BOOKING"


def test_two_students_can_book_different_desks(client, at):
    assert book(client, at(9), at(10), student_id="111", desk_id=1).status_code == 201
    assert book(client, at(9), at(10), student_id="222", desk_id=2).status_code == 201


# --- Desk and input checks ----------------------------------------------

def test_same_desk_same_time_is_rejected(client, at):
    assert book(client, at(9), at(11), student_id="111").status_code == 201
    r = book(client, at(10), at(12), student_id="222")
    assert r.status_code == 409
    assert r.get_json()["error"] == "DESK_TAKEN"


def test_unknown_desk_returns_404(client, at):
    assert book(client, at(9), at(10), desk_id=999).status_code == 404


def test_end_before_start_is_rejected(client, at):
    assert book(client, at(10), at(9)).status_code == 422


def test_start_in_the_past_is_rejected(client):
    from datetime import datetime
    r = book(client, datetime(2026, 11, 19, 9, 0), datetime(2026, 11, 19, 10, 0))
    assert r.status_code == 422
    assert r.get_json()["error"] == "START_IN_PAST"


def test_missing_student_id_is_rejected(client, at):
    r = book(client, at(9), at(10), student_id="")
    assert r.status_code == 422
    assert r.get_json()["message"] == "Please enter your student ID."
