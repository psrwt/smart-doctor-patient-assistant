from sqlalchemy.orm import Session, aliased
from app.db.models import Appointment, User


def get_doctor_appointments_stats(db: Session, doctor_id: str):
    """
    Fetch ALL appointments for a doctor with formatted date & time
    and patient/doctor names.
    """

    Doctor = aliased(User)
    Patient = aliased(User)

    rows = (
        db.query(
            Appointment.id.label("appointment_id"),
            Appointment.appointment_date,
            Appointment.start_time,
            Appointment.end_time,
            Appointment.status,
            Appointment.symptoms,
            Doctor.full_name.label("doctor_name"),
            Patient.full_name.label("patient_name"),
        )
        .join(Doctor, Doctor.id == Appointment.doctor_id)
        .join(Patient, Patient.id == Appointment.patient_id)
        .filter(Appointment.doctor_id == doctor_id)
        .order_by(Appointment.appointment_date, Appointment.start_time)
        .all()
    )

    result = []
    for r in rows:
        result.append(
            {
                "appointment_date": r.appointment_date.strftime("%d-%m-%y"),
                "start_time": r.start_time.strftime("%H:%M"),
                "end_time": r.end_time.strftime("%H:%M"),

                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "symptoms": r.symptoms,
                "doctor_name": r.doctor_name,
                "patient_name": r.patient_name,
            }
        )

    return result


def send_notification(message: str):
    """
    Sends a notification to frontend / console.
    No DB storage.
    """

    print("\n================ DOCTOR NOTIFICATION ================\n")
    print(message)
    print("\n=====================================================\n")

    return {
        "status": "sent",
        "message": "Notification delivered to doctor dashboard"
    }
    