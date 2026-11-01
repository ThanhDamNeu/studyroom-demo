"""Check-in rule (15 minutes) and the read-only endpoints."""
from datetime import timedelta

from studyroom import services

from conftest import NOW


def make_booking(app, start, end):
    with app.app_context():
        return services.create_booking("11225678", 1, start, end, now=NOW)


def try_checkin(app, booking_id, now):
    with app.app_context():
        return services.check_in(booking_id, now=now)


def test_checkin_15_minutes_after_start_is_allowed(app, at):
    b = make_booking(app, at(9), at(10))
    assert try_checkin(app, b["id"], at(9, 15))["status"] == "checked_in"


def test_checkin_16_minutes_after_start_is_rejected(app, at):
    b = make_booking(app, at(9), at(10))
    try:
        try_checkin(app, b["id"], at(9, 16))
        assert False, "expected BookingError"
    except services.BookingError as err:
        assert err.status == 422
        assert err.code == "CHECKIN_WINDOW"


def test_checkin_twice_is_rejected(app, at):
    b = make_booking(app, at(9), at(10))
    try_checkin(app, b["id"], at(9))
    try:
        try_checkin(app, b["id"], at(9) + timedelta(minutes=1))
        assert False, "expected BookingError"
    except services.BookingError as err:
        assert err.status == 409


def test_checkin_unknown_booking_returns_404(client):
    assert client.post("/api/bookings/999/checkin").status_code == 404


def test_desks_endpoint_lists_seed_desks(client):
    desks = client.get("/api/desks").get_json()
    assert [d["name"] for d in desks] == ["A-01", "A-02", "B-01", "B-02"]


def test_home_page_shows_title(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"<h1>StudyRoom" in r.data


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}
