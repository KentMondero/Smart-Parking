from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.models import Student, ClassSchedule, ParkingSlot, ParkingLog
from backend.models.schemas import ParkingRequest, ParkingResponse
from datetime import datetime
import pytz

PH_TZ = pytz.timezone("Asia/Manila")

def get_today_name() -> str:
    return datetime.now(PH_TZ).strftime("%A")

def student_has_class_today(db: Session, student_id: str) -> bool:
    """Check whether the student has any class scheduled for today."""
    today = get_today_name()
    schedules = (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.student_id == student_id,
            ClassSchedule.day_of_week == today,
        )
        .all()
    )
    return len(schedules) > 0


def student_has_class_now(db: Session, student_id: str) -> bool:
    """Check whether the student has a class happening right now (time-based)."""
    today = get_today_name()
    now   = datetime.now(PH_TZ).strftime("%H:%M")

    schedules = (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.student_id == student_id,
            ClassSchedule.day_of_week == today,
        )
        .all()
    )

    for schedule in schedules:
        if schedule.start_time <= now <= schedule.end_time:
            return True
    return False


def student_has_class_later(db: Session, student_id: str) -> bool:
    """Check whether the student has a class still coming up later today."""
    today = get_today_name()
    now   = datetime.now(PH_TZ).strftime("%H:%M")

    schedules = (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.student_id == student_id,
            ClassSchedule.day_of_week == today,
        )
        .all()
    )

    for schedule in schedules:
        if schedule.start_time > now:
            return True
    return False


def get_available_slots(db: Session):
    db.expire_all()
    return (
        db.query(ParkingSlot)
        .filter(ParkingSlot.status == "available")
        .order_by(ParkingSlot.slot_id)
        .all()
    )


def is_student_already_parked(db: Session, student_id: str) -> bool:
    """
    Check if student is currently parked by finding their most recent
    log entry and verifying that specific slot is still occupied.
    """
    latest_log = (
        db.query(ParkingLog)
        .filter(
            ParkingLog.student_id == student_id,
            ParkingLog.slot_id.isnot(None),
        )
        .order_by(ParkingLog.request_time.desc())
        .first()
    )

    if not latest_log or not latest_log.slot_id:
        return False

    slot = (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.slot_id == latest_log.slot_id,
            ParkingSlot.status == "occupied",
        )
        .first()
    )

    if not slot:
        return False

    most_recent_log_for_slot = (
        db.query(ParkingLog)
        .filter(ParkingLog.slot_id == slot.slot_id)
        .order_by(ParkingLog.request_time.desc())
        .first()
    )

    return most_recent_log_for_slot.student_id == student_id

def process_parking_request(db: Session, request: ParkingRequest) -> ParkingResponse:
    """
    Case 1a – Has ongoing class now + slot available   → park, ongoing class message
    Case 1b – Has class later today + slot available   → park, later class message
    Case 2  – No active/upcoming class + slot available→ park, no class message
    Case 3  – No active/upcoming class + no slots      → denied
    Case 4a – Has ongoing class now + no slots         → waitlisted
    Case 4b – Has class later today + no slots         → waitlisted
    """

    # ── Auto-register student if not in DB ───────────────────────────────────
    student = db.query(Student).filter(Student.student_id == request.student_id).first()
    if not student:
        student = Student(student_id=request.student_id, name=request.name)
        db.add(student)
        db.commit()
        db.refresh(student)

    # ── Duplicate check ───────────────────────────────────────────────────────
    if is_student_already_parked(db, request.student_id):
        return ParkingResponse(
            success=False,
            message="You are already parked. Please release your current slot first.",
            has_class_today=student_has_class_today(db, request.student_id),
        )

    # ── Evaluate class status ─────────────────────────────────────────────────
    has_class_now   = student_has_class_now(db, request.student_id)
    has_class_later = student_has_class_later(db, request.student_id)
    has_class_today = student_has_class_today(db, request.student_id)

    # Priority = has an ongoing OR upcoming class (not already finished)
    is_priority = has_class_now or has_class_later

    db.expire_all()  
    available_slots = get_available_slots(db)
    available_count = len(available_slots)

    # ── Case 3: No active/upcoming class + no slots ───────────────────────────
    if not is_priority and available_count == 0:
        message = "You cannot park and you don't have classes for today"
        log = ParkingLog(
            student_id=request.student_id,
            slot_id=None,
            response_message=message,
            has_class_today=has_class_today,
        )
        db.add(log)
        db.commit()
        return ParkingResponse(
            success=False,
            message=message,
            has_class_today=has_class_today,
        )

    # ── Case 1 & 2: Slot available ────────────────────────────────────────────
    if available_count > 0:
        slot = available_slots[0]
        slot.status = "occupied"

        if has_class_now:
            message = "You may park and you have an ongoing class right now"
        elif has_class_later:
            message = "You may park and you have classes scheduled later today"
        else:
            message = "You may park but you don't have classes today"

        log = ParkingLog(
            student_id=request.student_id,
            slot_id=slot.slot_id,
            response_message=message,
            has_class_today=has_class_today,
        )
        db.add(log)
        db.commit()
        db.refresh(slot)

        return ParkingResponse(
            success=True,
            message=message,
            slot_name=slot.slot_name,
            has_class_today=has_class_today,
        )

    # ── Case 4: Is priority but no slots ─────────────────────────────────────
    if has_class_now:
        message = "No slots available but you have an ongoing class. You may bring your vehicle and wait for an available slot."
    else:
        message = "No slots available but you have classes later today. You may bring your vehicle and wait for an available slot."

    log = ParkingLog(
        student_id=request.student_id,
        slot_id=None,
        response_message=message,
        has_class_today=has_class_today,
    )
    db.add(log)
    db.commit()
    return ParkingResponse(
        success=False,
        message=message,
        has_class_today=has_class_today,
    )


def release_parking_slot(db: Session, student_id: str) -> dict:
    log = (
        db.query(ParkingLog)
        .join(ParkingSlot, ParkingLog.slot_id == ParkingSlot.slot_id)
        .filter(
            ParkingLog.student_id == student_id,
            ParkingSlot.status == "occupied",
        )
        .order_by(ParkingLog.request_time.desc())
        .first()
    )

    if not log or not log.slot_id:
        return {"success": False, "message": "No active parking slot found for this student."}

    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == log.slot_id).first()
    if slot:
        slot.status = "available"
        db.commit()
        return {"success": True, "message": f"{slot.slot_name} has been released."}

    return {"success": False, "message": "Slot not found."}