import logging
from app.db.database import get_db
from app.mcp_server.tools.list_available_doctors import list_available_doctors
from app.mcp_server.tools.search_doctor_by_name import search_doctor_by_name
from app.mcp_server.tools.fetch_available_appointment_slots import fetch_available_appointment_slots
from app.mcp_server.tools.book_appointment import book_appointment

from app.mcp_server.tools.get_appointments_by_range import get_doctor_appointments_range
from app.mcp_server.tools.get_appointments_by_symptoms import search_appointments_by_symptoms

from app.db.database import SessionLocal

def run_check():
    db = SessionLocal()
    try:
        # slots = fetch_available_appointment_slots(db, "a9c65324-6666-467e-8a8d-3ce774b6a239", "2026-01-27")
        # print(slots)
        # result = book_appointment(db, "a9c65324-6666-467e-8a8d-3ce774b6a239", "cab2e060-9212-4766-8ca4-b97ba9828c83", "2026-01-26T11:00:00", "fever")
        # print(result)

        # result = get_doctor_appointments_range(db, "a9c65324-6666-467e-8a8d-3ce774b6a239", "2026-01-25", "2026-01-26")
        # print(result)

        result = search_appointments_by_symptoms(db, "a9c65324-6666-467e-8a8d-3ce774b6a239", "fever", "2026-01-25", "2026-01-26")
        print(result)

        

    finally:
        db.close()


if __name__ == "__main__":
    run_check()
