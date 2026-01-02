from django.core.mail import send_mail
from django.conf import settings

def send_due_rent_email(to_email, tenant_name, room_no, rent_due_date, rent_amount):
    subject = f"Rent Due Reminder for Room {room_no}"
    message = f"""
    Dear {tenant_name},

    This is a friendly reminder that your rent of ${rent_amount} for room {room_no} is due on {rent_due_date}.

    Please make sure to pay it on time.

    Thank you,
    Property Management Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False
    )
