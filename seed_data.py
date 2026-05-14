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
    {"student_id": "STU001", "name": "Alice Reyes",   "course": "BS Computer Science", "year_level": 3},
    {"student_id": "STU002", "name": "Ben Santos",    "course": "BS Information Technology", "year_level": 2},
    {"student_id": "STU003", "name": "Clara Dizon",   "course": "BS Engineering", "year_level": 4},
    {"student_id": "STU004", "name": "Dan Lim",       "course": "BS Business Administration", "year_level": 1},
    {"student_id": "STU005", "name": "Eva Mercado",   "course": "BS Nursing", "year_level": 3},
    {"student_id": "STU006", "name": "Franco dela Cruz", "course": "BS Architecture", "year_level": 2},
    {"student_id": "STU007", "name": "Grace Tan",     "course": "BS Education", "year_level": 4},
    {"student_id": "STU008", "name": "Hiro Nakamura", "course": "BS Computer Science", "year_level": 1},
]

for s in students:
    if not db.query(Student).filter(Student.student_id == s["student_id"]).first():
        db.add(Student(**s))

db.commit()

# ── Class Schedules ───────────────────────────────────────────────────────────
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

schedules = [
    
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