from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ── Student Schemas ──────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    student_id: str
    name: str
    course: Optional[str] = None
    year_level: Optional[int] = None


class StudentOut(BaseModel):
    student_id: str
    name: str
    course: Optional[str]
    year_level: Optional[int]

    class Config:
        from_attributes = True


# ── Schedule Schemas ─────────────────────────────────────────────────────────

class ScheduleCreate(BaseModel):
    student_id: str
    subject: str
    day_of_week: str  
    start_time: str    
    end_time: str      


class ScheduleOut(BaseModel):
    schedule_id: int
    student_id: str
    subject: str
    day_of_week: str
    start_time: str
    end_time: str

    class Config:
        from_attributes = True


# ── Parking Slot Schemas ─────────────────────────────────────────────────────

class ParkingSlotOut(BaseModel):
    slot_id: int
    slot_name: str
    status: str

    class Config:
        from_attributes = True


# ── Parking Request / Response ───────────────────────────────────────────────

class ParkingRequest(BaseModel):
    student_id: str
    name: str


class ParkingResponse(BaseModel):
    success: bool
    message: str
    slot_name: Optional[str] = None
    has_class_today: bool


# ── Parking Log Schemas ──────────────────────────────────────────────────────

class ParkingLogOut(BaseModel):
    log_id: int
    student_id: str
    student_name: Optional[str]
    slot_name: Optional[str]
    request_time: datetime
    response_message: str
    has_class_today: bool

    class Config:
        from_attributes = True


# ── Dashboard Stats ──────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_slots: int
    available_slots: int
    occupied_slots: int
    current_parked_students: List[dict]
