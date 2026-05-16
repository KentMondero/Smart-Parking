# Park U — Smart Parking Management System

A full-stack university parking system built with **FastAPI** (backend), **SQLite** (database), and **Streamlit** (frontend dashboard).

---

## Folder Structure

```
smart-parking/
├── backend/
│   ├── database/
│   │   └── database.py        # SQLAlchemy engine + session
│   ├── models/
│   │   ├── models.py          # ORM table definitions
│   │   └── schemas.py         # Pydantic request/response models
│   ├── routers/
│   │   ├── student_router.py  # /students endpoints
│   │   ├── schedule_router.py # /schedules endpoints
│   │   └── parking_router.py  # /parking endpoints + dashboard
│   ├── services/
│   │   └── parking_service.py # Core business logic
│   └── main.py                # FastAPI app entry point
├── frontend/
│   └── app.py                 # Streamlit dashboard
├── seed_data.py               # Sample data seeder
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python seed_data.py
```

This creates:
- **20 parking slots** (Slot-01 through Slot-20)
- **8 sample students** with class schedules
- Students with class today: STU001, STU002, STU003, STU005, STU007

### 3. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start the Streamlit frontend (new terminal)

```bash
streamlit run frontend/app.py
```

Dashboard opens at: [http://localhost:8501](http://localhost:8501)

---

## Parking Decision Logic

| Has Class Today | Slots Available | Result |
|---|---|---|
| ✅ Yes | ✅ Yes | **"You may park and you have classes today"** → Slot assigned |
| ❌ No | ✅ Yes | **"You may park but you don't have classes today"** → Slot assigned |
| ❌ No | ❌ No | **"You cannot park and you don't have classes for today"** → Denied |
| ✅ Yes | ❌ No | **"No slots available"** → Denied (rare edge case) |

---

## API Endpoints

### Students
| Method | Endpoint | Description |
|---|---|---|
| POST | `/students/` | Register a new student |
| GET | `/students/{student_id}` | Get student info |
| GET | `/students/` | List all students |

### Schedules
| Method | Endpoint | Description |
|---|---|---|
| POST | `/schedules/` | Add a class schedule |
| GET | `/schedules/today/{student_id}` | Get today's classes |
| GET | `/schedules/{student_id}` | Get all schedules |

### Parking
| Method | Endpoint | Description |
|---|---|---|
| POST | `/parking/request` | Request a parking slot |
| POST | `/parking/release/{student_id}` | Release a slot |
| GET | `/parking/slots` | All slots |
| GET | `/parking/slots/available` | Available slots |
| GET | `/parking/slots/occupied` | Occupied slots |
| GET | `/parking/logs` | Recent parking logs |
| GET | `/parking/dashboard` | Dashboard statistics |

---

## Frontend Features

- **Live Stats Bar** — Total / Available / Occupied slot counts
- **Visual Slot Map** — Green = available, Red = occupied
- **Parking Request Form** — Enter ID + Name, get instant response
- **Release Slot Button** — Free up your slot when leaving
- **Currently Parked Panel** — See who's in the lot right now
- **Parking Logs Table** — Full request history with class status badges
- **Auto-Refresh** — Dashboard updates every 5 seconds automatically
