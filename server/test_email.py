from dotenv import load_dotenv

load_dotenv()

from app.services.email_service import send_appointment_confirmation_email


send_appointment_confirmation_email(
    to_email="kirankiranrawat8@gmail.com",
    patient_name="John Doe",
    doctor_name="Dr. Smith",
    appointment_date="2022-01-01",
    start_time="10:00 AM",
    end_time="11:00 AM",
)
