from langchain_core.tools import tool
from sqlalchemy.orm import Session
from app.mcp.tools import (
    fetch_doctors_from_db,
    fetch_doctor_availability,
    make_appointment,
)


class MCPToolRegistry:
    def __init__(self, db: Session):
        self.db = db

    def get_tools(self, current_user):
        @tool
        def list_doctors():
            """Get a list of all available doctors and their details."""
            return fetch_doctors_from_db(self.db)

        @tool
        def check_doctor_availability(doctor_name: str):
            """Check the availability of a specific doctor."""
            return fetch_doctor_availability(self.db, doctor_name)

        @tool
        def book_appointment(
            doctor_name: str, appointment_date: str, start_time: str, end_time: str
        ):
            """Make an appointment with a specific doctor."""
            return make_appointment(
                db=self.db,
                doctor_name=doctor_name,
                patient_id=current_user["id"],
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
            )

        # ROLE-BASED TOOL DISCOVERY (Agentic Logic)

        return [list_doctors, check_doctor_availability, book_appointment]
