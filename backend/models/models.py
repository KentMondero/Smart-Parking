from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course = Column(String, nullable=True)
    year_level = Column(Integer, nullable=True)

    schedules = relationship("ClassSchedule", back_populates="student")
    parking_logs = relationship("ParkingLog", back_populates="student")


class ClassSchedule(Base):
    __tablename__ = "class_schedules"

    schedule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    subject = Column(String, nullable=False)
    day_of_week = Column(String, nullable=False)  
    start_time = Column(String, nullable=False)   
    end_time = Column(String, nullable=False)     

    student = relationship("Student", back_populates="schedules")


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    slot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_name = Column(String, unique=True, nullable=False)
    status = Column(String, default="available")  

    parking_logs = relationship("ParkingLog", back_populates="slot")


class ParkingLog(Base):
    __tablename__ = "parking_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id"), nullable=True)
    request_time = Column(DateTime, default=datetime.now)
    response_message = Column(String, nullable=False)
    has_class_today = Column(Boolean, default=False)

    student = relationship("Student", back_populates="parking_logs")
    slot = relationship("ParkingSlot", back_populates="parking_logs")
