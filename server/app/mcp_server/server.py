from fastmcp import FastMCP
from app.db.database import SessionLocal
import logging
import sys

# tools
from app.mcp_server.tools.list_available_doctors import list_available_doctors
from app.mcp_server.tools.search_doctor_by_name import search_doctor_by_name
from app.mcp_server.tools.fetch_available_appointment_slots import fetch_available_appointment_slots
from app.mcp_server.tools.book_appointment import book_appointment

from app.mcp_server.tools.get_appointments_by_range import get_doctor_appointments_range
from app.mcp_server.tools.get_appointments_by_symptoms import search_appointments_by_symptoms
from app.mcp_server.tools.notify_on_slack import notify_on_slack

# Configure logging to see INFO level logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)

# initialize the MCP server
mcp = FastMCP("DoctorPatientAssistant")


@mcp.tool()
async def get_doctors() -> dict:
    """
    Fetches a list of all registered doctors in the system.
    Use this tool when the user wants to see which doctors are available.
    """
    with SessionLocal() as db:
        return list_available_doctors(db)

@mcp.tool()
async def find_doctor(name: str) -> dict:
    """
    Finds a specific doctor's unique ID and profile using their name.
    Use this tool IMMEDIATELY when a user mentions a doctor's name (e.g., 'Dr. Smith' or 'Ahuja').
    You MUST have the doctor_id returned by this tool before you can check slots or book appointments.
    """
    with SessionLocal() as db:
        return search_doctor_by_name(db, name)

@mcp.tool()
async def get_available_slots(doctor_id: str, date_str: str) -> dict:
    """
    Retrieves available 1-hour appointment windows for a specific doctor on a specific date.
    Trigger this when a user selects a doctor and asks 'When is he free?' or 'Check slots for tomorrow'.
    :param doctor_id: The UUID of the doctor (get this from find_doctor).
    :param date_str: The date in YYYY-MM-DD format (IST).
    """
    with SessionLocal() as db:
        return fetch_available_appointment_slots(db, doctor_id, date_str)

@mcp.tool()
async def book_new_appointment(doctor_id: str, patient_id: str, start_at: str, symptoms: str) -> dict:
    """
    Finalizes and books a medical appointment in the database and Google Calendar.
    Use this ONLY after the user has confirmed a specific time slot from get_available_slots.
    :param start_at: The ISO format start time (e.g., '2026-01-25T14:00:00+05:30') provided by the slot tool.
    :param symptoms: A brief description of the patient's condition.
    """
    with SessionLocal() as db:
        return book_appointment(db, doctor_id, patient_id, start_at, symptoms)

@mcp.tool()
async def get_doctor_appointments_by_date_range(doctor_id: str, start_date_str: str, end_date_str: str) -> dict:
    """
    Fetches a summary of appointments for a doctor within a specific date range.
    Use this when a doctor asks 'What does my week look like?' or 'List my appointments for today'.
    This groups appointments by date and provides complete appointment informatino with slot times, patient names and symptoms.
    :param doctor_id: The UUID of the doctor.
    :param start_date_str: The start date in YYYY-MM-DD format.
    :param end_date_str: The end date in YYYY-MM-DD format.
    Returns a summary including total count and a schedule breakdown.
    """
    with SessionLocal() as db:
        return get_doctor_appointments_range(db, doctor_id, start_date_str, end_date_str)

@mcp.tool()
async def search_appointments_by_symptom_keyword(doctor_id: str, symptom_keyword: str, start_date_str: str, end_date_str: str) -> dict:
    """
    Searches for appointments where the patient's symptoms match a keyword.
    Use this for clinical reporting, e.g., 'How many patients with fever did I see this month?' 
    or 'Find all patients mentioning back pain'.
    :param doctor_id: The UUID of the doctor.
    :param symptom_keyword: The keyword to search for in symptoms (e.g., 'fever', 'cough').
    :param start_date_str: The start date in YYYY-MM-DD format.
    :param end_date_str: The end date in YYYY-MM-DD format.
    Returns a list of matching appointments with patient details.
    """
    with SessionLocal() as db:
        return search_appointments_by_symptoms(db, doctor_id, symptom_keyword, start_date_str, end_date_str)

@mcp.tool()
async def send_summary_report_to_slack(doctor_id: str, content: str) -> dict:
    """
    Sends a summary, schedule, or patient report directly to a doctor's Slack.
    Use this ONLY when the user explicitly asks to 'send to slack', 'notify me', or 'push to slack'.
    :param doctor_id: The UUID of the doctor.
    :param content: The actual text/report to send.
    """
    with SessionLocal() as db:
        return notify_on_slack(db, doctor_id, content)






if __name__ == "__main__":
    mcp.run(transport="stdio")
    