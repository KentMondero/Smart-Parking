from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database.database import get_db
from backend.models.models import ParkingSlot, ParkingLog, Student
from backend.models.schemas import ParkingRequest, ParkingResponse, ParkingSlotOut, ParkingLogOut, DashboardStats
from backend.services.parking_service import process_parking_request, release_parking_slot

router = APIRouter(prefix="/parking", tags=["Parking"])


def _duration_str(parked_since: datetime) -> str:
    delta = datetime.now() - parked_since
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@router.post("/request", response_model=ParkingResponse)
def request_parking(request: ParkingRequest, db: Session = Depends(get_db)):
    return process_parking_request(db, request)


@router.post("/release/{student_id}")
def release_slot(student_id: str, db: Session = Depends(get_db)):
    result = release_parking_slot(db, student_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.get("/slots/available", response_model=list[ParkingSlotOut])
def available_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).filter(ParkingSlot.status == "available").all()


@router.get("/slots/occupied", response_model=list[ParkingSlotOut])
def occupied_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).filter(ParkingSlot.status == "occupied").all()


@router.get("/slots", response_model=list[ParkingSlotOut])
def all_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).order_by(ParkingSlot.slot_id).all()


@router.get("/logs", response_model=list[ParkingLogOut])
def parking_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(ParkingLog)
        .order_by(ParkingLog.request_time.desc())
        .limit(500)
        .all()
    )
    result = []
    for log in logs:
        student = db.query(Student).filter(Student.student_id == log.student_id).first()
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == log.slot_id).first() if log.slot_id else None
        result.append(
            ParkingLogOut(
                log_id=log.log_id,
                student_id=log.student_id,
                student_name=student.name if student else "Unknown",
                slot_name=slot.slot_name if slot else "N/A",
                request_time=log.request_time,
                response_message=log.response_message,
                has_class_today=log.has_class_today,
            )
        )
    return result


@router.get("/profile/{student_id}")
def student_profile(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    logs = (
        db.query(ParkingLog)
        .filter(ParkingLog.student_id == student_id)
        .order_by(ParkingLog.request_time.desc())
        .all()
    )
    history = []
    for log in logs:
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == log.slot_id).first() if log.slot_id else None
        history.append({
            "log_id": log.log_id,
            "slot_name": slot.slot_name if slot else "N/A",
            "request_time": log.request_time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_message": log.response_message,
            "has_class_today": log.has_class_today,
        })
    total_requests = len(logs)
    approved = sum(1 for l in logs if l.slot_id is not None)
    denied = total_requests - approved
    return {
        "student_id": student.student_id,
        "name": student.name,
        "course": student.course,
        "year_level": student.year_level,
        "total_requests": total_requests,
        "approved": approved,
        "denied": denied,
        "history": history,
    }


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(ParkingSlot).count()
    available = db.query(ParkingSlot).filter(ParkingSlot.status == "available").count()
    occupied = db.query(ParkingSlot).filter(ParkingSlot.status == "occupied").count()
    occupied_slots = db.query(ParkingSlot).filter(ParkingSlot.status == "occupied").all()
    current_parked = []
    for slot in occupied_slots:
        log = (
            db.query(ParkingLog)
            .filter(ParkingLog.slot_id == slot.slot_id)
            .order_by(ParkingLog.request_time.desc())
            .first()
        )
        if log:
            student = db.query(Student).filter(Student.student_id == log.student_id).first()
            current_parked.append({
                "student_id": log.student_id,
                "student_name": student.name if student else "Unknown",
                "slot_name": slot.slot_name,
                "parked_since": log.request_time.strftime("%H:%M:%S"),
                "parked_since_iso": log.request_time.isoformat(),
                "duration": _duration_str(log.request_time),
                "has_class_today": log.has_class_today,
            })
    return DashboardStats(
        total_slots=total,
        available_slots=available,
        occupied_slots=occupied,
        current_parked_students=current_parked,
    )

@router.get("/slots/available", response_model=list[ParkingSlotOut])
def available_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).filter(ParkingSlot.status == "available").order_by(ParkingSlot.slot_id).all()


@router.get("/slots/occupied", response_model=list[ParkingSlotOut])
def occupied_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).filter(ParkingSlot.status == "occupied").order_by(ParkingSlot.slot_id).all()


@router.get("/slots", response_model=list[ParkingSlotOut])
def all_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).filter().order_by(ParkingSlot.slot_id).all()