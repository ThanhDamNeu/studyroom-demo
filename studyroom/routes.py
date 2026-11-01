"""HTTP layer only: read the request, call a service, return JSON."""
from flask import Blueprint, current_app, jsonify, render_template, request

from . import repository, services
from .services import BookingError

bp = Blueprint("studyroom", __name__)

PAGE_TITLE = "StudyRoom"   # Demo 4 (slide 31): change this line and time the full loop


@bp.errorhandler(BookingError)
def handle_booking_error(err):
    return jsonify(error=err.code, message=err.message), err.status


@bp.get("/")
def index():
    return render_template("index.html", title=PAGE_TITLE)


@bp.get("/api/health")
def health():
    return jsonify(status="ok")


@bp.get("/api/desks")
def get_desks():
    return jsonify(repository.list_desks())


@bp.post("/api/bookings")
def post_booking():
    body = request.get_json(silent=True) or {}
    booking = services.create_booking(
        student_id=str(body.get("student_id", "")).strip(),
        desk_id=body.get("desk_id"),
        start=services.parse_time(body.get("start"), "start"),
        end=services.parse_time(body.get("end"), "end"),
        now=current_app.config["CLOCK"](),
    )
    return jsonify(booking), 201


@bp.post("/api/bookings/<int:booking_id>/checkin")
def post_checkin(booking_id):
    return jsonify(services.check_in(booking_id, now=current_app.config["CLOCK"]()))
