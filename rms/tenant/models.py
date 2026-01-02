from django.db import models
from django.utils import timezone
from typing import TYPE_CHECKING
from django.db.models import QuerySet

# Create your models here.

class Tenant(models.Model):
    if TYPE_CHECKING:
        id: int
        payments: QuerySet['Payment']
    room = models.OneToOneField('property.Room', on_delete=models.CASCADE, related_name='tenant')
    tenant_name = models.CharField(max_length=150)
    phone_no = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    lease_start_date = models.DateField(blank=True, null=True)
    lease_end_date = models.DateField(blank=True, null=True)
    rent_due_date = models.DateField()
    
    id_proof_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Passport", "Citizenship"
    id_proof_number = models.CharField(max_length=100, blank=True, null=True)

    def is_rent_due(self):
        return self.rent_due_date <= timezone.now().date()
    
    def total_paid(self):
        return self.payments.filter(status='paid').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def outstanding_balance(self):
        return self.payments.filter(status='pending').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def payment_history_summary(self):
        """Returns a summary of payment history"""
        return {
            'total_paid': self.total_paid(),
            'outstanding': self.outstanding_balance(),
            'total_payments': self.payments.count(),
            'paid_payments': self.payments.filter(status='paid').count(),
            'pending_payments': self.payments.filter(status='pending').count(),
            'overdue_payments': self.payments.filter(status='overdue').count(),
        }

    def __str__(self):
        return self.tenant_name


class Payment(models.Model):
    if TYPE_CHECKING:
        id: int
    
    payment_status = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    
    payment_method = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    room = models.ForeignKey('property.Room', on_delete=models.CASCADE, related_name='payments')
    property = models.ForeignKey('property.Property', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=payment_method)
    status = models.CharField(max_length=20, choices=payment_status, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.tenant.tenant_name} - {self.amount} ({self.payment_date.date()})"
    
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status == 'paid':
            return False
        return self.tenant.rent_due_date < timezone.now().date()