from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database.database import get_db
from backend.models.models import ClassSchedule, Student
from backend.models.schemas import ScheduleCreate, ScheduleOut

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("/", response_model=ScheduleOut)
def add_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == schedule.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    new_schedule = ClassSchedule(**schedule.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("/today/{student_id}", response_model=list[ScheduleOut])
def get_today_schedules(student_id: str, db: Session = Depends(get_db)):
    today = datetime.now().strftime("%A")
    schedules = (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.student_id == student_id,
            ClassSchedule.day_of_week == today,
        )
        .all()
    )
    return schedules


@router.get("/{student_id}", response_model=list[ScheduleOut])
def get_all_schedules(student_id: str, db: Session = Depends(get_db)):
    return db.query(ClassSchedule).filter(ClassSchedule.student_id == student_id).all()
