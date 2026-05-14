from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine
from backend.models.models import Base
from backend.routers import student_router, schedule_router, parking_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Parking Management System",
    description="University Smart Parking API — manages student parking with class schedule priority.",
    version="1.0.0",
)

# Allow Streamlit (localhost) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router.router)
app.include_router(schedule_router.router)
app.include_router(parking_router.router)


@app.get("/")
def root():
    return {
        "message": "Smart Parking Management System API is running.",
        "docs": "/docs",
    }
