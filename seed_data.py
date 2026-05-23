"""
Seed the database with sample students, schedules, and parking slots.
Run once: python seed_data.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.database import SessionLocal, engine
from backend.models.models import Base, Student, ClassSchedule, ParkingSlot
from datetime import datetime

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Parking Slots ─────────────────────────────────────────────────────────────
slots = [f"Slot-{i:02d}" for i in range(1, 51)]   
for name in slots:
    if not db.query(ParkingSlot).filter(ParkingSlot.slot_name == name).first():
        db.add(ParkingSlot(slot_name=name, status="available"))

# ── Students ──────────────────────────────────────────────────────────────────
students = [
    {"student_id": "2024-200354", "name": "Kent Mondero",    "course": "BS Information Technology", "year_level": 2},
    {"student_id": "2024-200372", "name": "Jerome Santos",   "course": "BS Information Technology", "year_level": 2},
    {"student_id": "2024-200413", "name": "Rafael Cutamora", "course": "BS Information Technology", "year_level": 2},
    {"student_id": "2024-200374", "name": "Lorenz Mangalino","course": "BS Information Technology", "year_level": 2},
    {"student_id": "2024-200399", "name": "Lyca Jangas",     "course": "BS Information Technology", "year_level": 2},
    {"student_id": "2024-200382", "name": "Joshua Malana",   "course": "BS Information Technology", "year_level": 2},
    {"student_id": "1234", "name": "Lebron", "course": "IT", "year_level": 2},
]

for s in students:
    if not db.query(Student).filter(Student.student_id == s["student_id"]).first():
        db.add(Student(**s))

db.commit()

# ── Class Schedules ───────────────────────────────────────────────────────────
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

schedules = [
    # Lebron
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Monday",    "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Tuesday",   "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Wednesday", "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Thursday",  "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Friday",    "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Saturday",  "start_time": "01:00", "end_time": "23:00"},
    {"student_id": "1234", "subject": "Basketball", "day_of_week": "Sunday",  "start_time": "01:00", "end_time": "23:00"},

    # Kent  
    {"student_id": "2024-200354", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200354", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200354", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200354", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200354", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200354", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},

    # Jerome 
    {"student_id": "2024-200372", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200372", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200372", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200372", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200372", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200372", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},
    
    # Rafael
    {"student_id": "2024-200413", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200413", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200413", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},

    # Lorenz
    {"student_id": "2024-200413", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200413", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200413", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},

   # Lyca
    {"student_id": "2024-200413", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200413", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200413", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},

   # Joshua
    {"student_id": "2024-200413", "subject": "Networking 1",           "day_of_week": "Monday",  "start_time": "13:00", "end_time": "16:00"},
    {"student_id": "2024-200413", "subject": "Quantitative Methods",   "day_of_week": "Monday",  "start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Multimedia",             "day_of_week": "Thursday","start_time": "09:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "Computer Graphics",      "day_of_week": "Thursday","start_time": "13:00", "end_time": "15:00"},
    {"student_id": "2024-200413", "subject": "Integrative Programming","day_of_week": "Saturday","start_time": "07:00", "end_time": "12:00"},
    {"student_id": "2024-200413", "subject": "PE04",                   "day_of_week": "Saturday","start_time": "13:00", "end_time": "15:00"},
]

for sc in schedules:
    exists = db.query(ClassSchedule).filter(
        ClassSchedule.student_id == sc["student_id"],
        ClassSchedule.subject == sc["subject"],
        ClassSchedule.day_of_week == sc["day_of_week"],
    ).first()
    if not exists:
        db.add(ClassSchedule(**sc))

db.commit()
db.close()

print("Seed data inserted successfully!")
print(f"   • 20 parking slots created")
print(f"   • {len(students)} students registered")
print(f"   • {len(schedules)} class schedules added")