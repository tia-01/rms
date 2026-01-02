from django.db import models
from tenant.models import Payment, Tenant
from django.conf import settings
# Create your models here.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

class Property(models.Model):
    if TYPE_CHECKING:
        rooms: QuerySet['Room']
        payments: QuerySet['Payment']
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    # image_height = models.PositiveIntegerField(null=True, blank=True)
    # image_width = models.PositiveIntegerField(null=True, blank=True)
    # height_field='image_height', width_field='image_width',
    image = models.ImageField(upload_to='property_images/', blank=True, max_length=None)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"
    
    def total_rent_due(self):
        """Sum of all room rents"""
        return sum(room.rent_amount for room in self.rooms.all())
    
    def total_rent_collected(self):
        """Sum of all payments for this property"""
        from django.db.models import Sum
        return self.payments.aggregate(total=Sum('amount'))['total'] or 0
    
    def total_rent_pending(self):
        """Difference between due and collected rent"""
        return self.total_rent_due() - self.total_rent_collected()
    

class Room(models.Model):
    if TYPE_CHECKING:
        id: int
        tenant: 'Tenant'
        payments: QuerySet['Payment']
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_no = models.CharField(max_length=50)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.property.name} - Room {self.room_no}"
    
    class Meta:
        unique_together = ['property', 'room_no']
    
    