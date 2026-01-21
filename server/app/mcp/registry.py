# app/mcp/registry.py
from sqlalchemy.orm import Session
from langchain_core.tools import tool
from app.mcp.tools import (
    fetch_doctors_from_db,
    fetch_doctor_availability,
    make_appointment,
    book_google_calendar_event,
)


class MCPToolRegistry:
    def __init__(self, db: Session):
        self.db = db

    def get_tools(self, current_user):
        @tool
        def list_doctors():
            """Get a list of all available doctors"""
            return fetch_doctors_from_db(self.db)

        @tool
        def check_doctor_availability(doctor_name: str):
            """Check the availability of a specific doctor for appointments."""
            return fetch_doctor_availability(self.db, doctor_name)

        @tool
        def book_appointment_tool(
            doctor_name: str, appointment_date: str, start_time: str, end_time: str
        ):
            """Make an appointment with a specific doctor in the database.
            appointment_date: YYYY-MM-DD
            start_time: HH:MM (24-hour)
            end_time: HH:MM (24-hour)
            """
            return make_appointment(
                db=self.db,
                doctor_name=doctor_name,
                patient_id=current_user["id"],
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
            )

        @tool
        def book_google_calendar_tool(doctor_name: str, start_time: str, end_time: str):
            """Book an appointment in Google Calendar.
            start_time/end_time: flexible strings like '2026-01-22 15:00' or ISO '2026-01-22T15:00:00+05:30'"""
            return book_google_calendar_event(doctor_name, start_time, end_time)

        # Role-based tools (agent can pick based on user role)
        return [
            list_doctors,
            check_doctor_availability,
            book_appointment_tool,
            book_google_calendar_tool,
        ]
