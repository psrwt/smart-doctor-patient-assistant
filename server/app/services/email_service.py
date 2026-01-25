import os
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_appointment_email_confirmation(to_email, patient_name, doctor_name, start_at, end_at):
   
    subject = "📅 Appointment Confirmed - Doctor Patient Assistant"

    # Formatting inside the function ensures the email always looks consistent
    date_str = start_at.strftime("%B %d, %Y")
    time_range = f"{start_at.strftime('%I:%M %p')} - {end_at.strftime('%I:%M %p')}"

    body = f"""Hi {patient_name},
Your appointment with {doctor_name} is confirmed.

        Details:
        Date: {date_str}
        Time: {time_range}

        Please arrive 10 minutes early.
    """

    # --- KEEP YOUR TEST MODE ---
    if os.getenv("EMAIL_TEST_MODE", "true").lower() == "true":
        logger.info(f"TEST MODE: Email to {to_email} suppressed. Body: {body}")
        return True

    # --- PRODUCTION SENDING ---
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = EmailMessage()
    msg["From"] = f"Smart Clinic <{smtp_user}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        # Added a 10-second timeout so the tool doesn't hang forever
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            return True
    except Exception as e:
        # We raise the error so 'book_appointment_atomic' knows to ROLLBACK
        raise RuntimeError(f"SMTP Error: {str(e)}")