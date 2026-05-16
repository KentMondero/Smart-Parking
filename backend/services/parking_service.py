from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.models import Student, ClassSchedule, ParkingSlot, ParkingLog
from backend.models.schemas import ParkingRequest, ParkingResponse


def get_today_name() -> str:
    """Return today's day name, e.g. 'Monday'."""
    return datetime.now().strftime("%A")

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
    now   = datetime.now().strftime("%H:%M")

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


def get_available_slots(db: Session):
    return (
        db.query(ParkingSlot)
        .filter(ParkingSlot.status == "available")
        .all()
    )


def count_available_slots(db: Session) -> int:
    return (
        db.query(ParkingSlot)
        .filter(ParkingSlot.status == "available")
        .count()
    )


def is_student_already_parked(db: Session, student_id: str) -> bool:
    """Prevent duplicate parking — check if student already has an active slot."""
    active_log = (
        db.query(ParkingLog)
        .join(ParkingSlot, ParkingLog.slot_id == ParkingSlot.slot_id, isouter=True)
        .filter(
            ParkingLog.student_id == student_id,
            ParkingSlot.status == "occupied",
        )
        .first()
    )
    return active_log is not None


def process_parking_request(db: Session, request: ParkingRequest) -> ParkingResponse:
    """
    Core decision engine.

    Case 1 – Priority   : has class today + slot available  → park, priority message
    Case 2 – Non-priority: no class today + slot available  → park, non-priority message
    Case 3 – Denied     : no class today + no slots left    → deny
    Case 4 – Waitlisted : has class today + no slots left   → waiting
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

    has_class_today = student_has_class_today(db, request.student_id)
    has_class_now   = student_has_class_now(db, request.student_id)
    has_class       = has_class_today    
    available_slots = get_available_slots(db)
    available_count = len(available_slots)

    # ── Case 3: No class today + no slots ────────────────────────────────────
    if not has_class_today and available_count == 0:
        message = "You cannot park and you don't have classes for today"
        log = ParkingLog(
            student_id=request.student_id,
            slot_id=None,
            response_message=message,
            has_class_today=has_class,
        )
        db.add(log)
        db.commit()
        return ParkingResponse(success=False, message=message, has_class_today=has_class)

    # ── Case 1 & 2: Slot available ────────────────────────────────────────────
    if available_count > 0:
        slot = available_slots[0]
        slot.status = "occupied"

        if has_class_now:
            message = "You may park and you have an ongoing class right now"
        elif has_class_today:
            message = "You may park and you have classes scheduled later today"
        else:
            message = "You may park but you don't have classes today"

        log = ParkingLog(
            student_id=request.student_id,
            slot_id=slot.slot_id,
            response_message=message,
            has_class_today=has_class,
        )
        db.add(log)
        db.commit()
        db.refresh(slot)

        return ParkingResponse(
            success=True,
            message=message,
            slot_name=slot.slot_name,
            has_class_today=has_class,
        )

    # ── Case 4: Has class but no slots ───────────────────────────────────────
    if has_class_now:
        message = "No slots available but you have an ongoing class. You may bring your vehicle and wait for an available slot."
    else:
        message = "No slots available but you have classes later today. You may bring your vehicle and wait for an available slot."
    log = ParkingLog(
        student_id=request.student_id,
        slot_id=None,
        response_message=message,
        has_class_today=has_class,
    )
    db.add(log)
    db.commit()
    return ParkingResponse(success=False, message=message, has_class_today=has_class)


def release_parking_slot(db: Session, student_id: str) -> dict:
    """Mark a student's current slot as available again."""
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
        return {"success": True, "message": f"Slot {slot.slot_name} has been released."}

    return {"success": False, "message": "Slot not found."}
