from django.utils import timezone
from .models import Tenant
from .utils import send_due_rent_email

def send_due_rent_emails():
    today = timezone.now().date()
    tenants_due = Tenant.objects.filter(rent_due_date=today, is_active=True)

    for tenant in tenants_due:
        if tenant.room and tenant.email:
            send_due_rent_email(
                to_email=tenant.email,
                tenant_name=tenant.tenant_name,
                room_no=tenant.room.room_no,
                rent_due_date=tenant.rent_due_date,
                rent_amount=tenant.room.rent_amount
            )
