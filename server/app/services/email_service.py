import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_appointment_confirmation_email(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    start_time: str,
    end_time: str,
):
    subject = "Appointment Confirmed"

    body = f"""
Hi {patient_name},

Your appointment with {doctor_name} has been booked successfully.

Appointment Details:
Date: {appointment_date}
Time: {start_time} to {end_time}

Please arrive 10 minutes early.

Thank you,
Smart Doctor Assistant
"""

    # ---------- DEV MODE ----------
    if os.getenv("EMAIL_TEST_MODE", "true").lower() == "true":
        print("=== APPOINTMENT CONFIRMATION EMAIL (TEST MODE) ===")
        print(f"To: {to_email}")
        print(body)
        print("===============================================")
        return

    # ---------- PROD MODE ----------
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "0"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        raise RuntimeError("SMTP configuration missing in environment variables")

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        print("Email sending failed:", str(e))
