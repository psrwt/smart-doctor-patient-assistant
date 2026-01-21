from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Appointment
from app.mcp.tools.doctor_tools import get_doctor_appointments_stats  # adjust import
from uuid import UUID

# 👉 replace with an actual doctor UUID from your DB
TEST_DOCTOR_ID = "a30dda33-11e8-4a0d-b191-f2ac211b2864"


def main():
    db: Session = SessionLocal()

    try:
        print("Fetching all appointments for doctor:", TEST_DOCTOR_ID)

        results = get_doctor_appointments_stats(db, TEST_DOCTOR_ID)

        print(results)

    finally:
        db.close()


if __name__ == "__main__":
    main()
