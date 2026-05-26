# Park-U — Smart Parking Management System

A university parking system built with **FastAPI** (backend), **SQLite** & **PostgreSQL** (database), and **Streamlit** (frontend dashboard).

---

## Folder Structure

```
smart-parkingv2/
├── backend/
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py              # ORM table definitions
│   │   └── schemas.py             # Pydantic request/response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── student_router.py      # /students endpoints
│   │   ├── schedule_router.py     # /schedules endpoints
│   │   └── parking_router.py      # /parking endpoints + dashboard + profile
│   ├── services/
│   │   ├── __init__.py
│   │   └── parking_service.py     # Core business logic
│   ├── __init__.py
│   └── main.py                    # FastAPI app entry point
├── frontend/
│   ├── app.py                     # Streamlit dashboard
│   └── Logo.png                   # University logo (header + browser tab)
├── seed_data.py                   # Sample data seeder
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
python3 seed_data.py
```

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

> Always run both commands from the project root folder (`smart-parkingv2/`) so the database path resolves correctly.

---

## Cloud Deployment (Render)

The app is deployed at: https://park-u.onrender.com
API docs available at: https://park-u.onrender.com/docs

### Setup
1. Create a PostgreSQL database on Render
2. Add environment variable in your web service:
   - Key: `DATABASE_URL`
   - Value: Internal Database URL from Render
3. Push to GitHub — Render auto-deploys on every push

### Seed the cloud database from local machine
```bash
DATABASE_URL="postgresql://...external_url..." python3 seed_data.py
```

> Use the **External Database URL** when seeding from your local machine.
> Use the **Internal Database URL** as the environment variable on Render.

---

## Resetting the Database

To wipe all data and start fresh:

```bash
# Local (SQLite)
rm smart_parking.db
python3 seed_data.py

# Cloud (PostgreSQL on Render)
# Step 1 — Clear all tables
DATABASE_URL="postgresql://...external_url..." python3 -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://...external_url...')
with engine.connect() as conn:
    conn.execute(text('TRUNCATE TABLE parking_logs, parking_slots, class_schedules, students RESTART IDENTITY CASCADE'))
    conn.commit()
print('Database cleared!')
"

# Step 2 — Re-seed
DATABASE_URL="postgresql://...external_url..." python3 seed_data.py
```

> This permanently deletes all parking logs, slot statuses, and any students added through the app.

---

## Parking Decision Logic

The system evaluates two conditions on every request:
- Does the student have a class **right now** or **later today**?
- Are parking slots available?

| Case | Condition | Result |
|---|---|---|
| 1a | Class ongoing now + slot available | **"You may park and you have an ongoing class right now"** |
| 1b | Class later today + slot available | **"You may park and you have classes scheduled later today"** |
| 2 | No active/upcoming class + slot available | **"You may park but you don't have classes today"** |
| 3 | No active/upcoming class + no slots | **"You cannot park and you don't have classes for today"** |
| 4a | Class ongoing now + no slots | **"No slots available but you have an ongoing class. You may bring your vehicle and wait."** |
| 4b | Class later today + no slots | **"No slots available but you have classes later today. You may bring your vehicle and wait."** |

> **Priority rule:** A student is considered priority only if their class is **currently ongoing** or **still upcoming** — classes that have already ended do not grant priority status.

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
| GET | `/parking/slots/available` | Available slots only |
| GET | `/parking/slots/occupied` | Occupied slots only |
| GET | `/parking/logs` | Recent parking logs (last 500) |
| GET | `/parking/profile/{student_id}` | Full parking history for one student |
| GET | `/parking/dashboard` | Live dashboard statistics |

---

## Frontend Features

### Dashboard Tab
- **Capacity bar** — shows percentage of slots used, color shifts green → yellow → red
- **Live stat cards** — Total, Available, and Occupied slot counts
- **Parking request form** — Enter Student ID and Name to request a slot
- **Side-by-side buttons** — Request Parking and Release My Slot shown together
- **Color-coded slot map** — 🟢 Available, 🔴 Occupied, auto-refreshes every 5 seconds
- **Dark / Light mode toggle** — defaults to light mode, toggle to dark anytime

### Admin Tab (Password Protected)
- **Admin login gate** — password required to access; session persists until logout
- **Logout button** — locks the admin section when done
- **Parking logs table** — full request history with student name, slot, time, and class status badges
- **Search / filter logs** — filter by student name, ID, or date (`YYYY-MM-DD`)
- **Export to CSV** — download all parking logs as a timestamped `.csv` file
- **Student profile lookup** — search any student by ID to view their stats and full parking history
- **Profile stats** — total requests, approved count, denied count per student

---

## Sample Students for Testing

Use these IDs from your seed data to test all parking cases:

| Student ID | Name | Has Class Today |
|---|---|---|
| `2024-200354` | Kent Mondero | Depends on schedule |
| `2024-200372` | Jerome Santos | Depends on schedule |
| `2024-200413` | Rafael Cutamora | Depends on schedule |
| `2024-200374` | Lorenz Mangalino | Depends on schedule |
| `2024-200399` | Lyca Jangas | Depends on schedule |
| `2024-200382` | Joshua Malana | Depends on schedule |
| `1234` | Every day (all 7 days seeded) |
