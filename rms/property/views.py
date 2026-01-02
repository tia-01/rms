from rest_framework import viewsets
from .models import Property, Room, Tenant, Payment
from .serializers import PropertySerializer, RoomSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .notifications import send_due_rent_emails
from django.db.models import Sum
from django.utils import timezone

# Create your views here.

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    
    # def get_queryset(self):
    #     return Property.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()
        
@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def send_due_rent_view(request):
    send_due_rent_emails()
    return Response({
        "status": True,
        "message": "Due rent emails have been sent."
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def housewise_overview(request):
    """ total rent collected and pending for each property """
    overview = []
    properties = Property.objects.filter(owner=request.user)
    
    for prop in properties:
        overview.append({
            "property": prop.name,
            "total_rent_due": prop.total_rent_due(),
            "total_collected": prop.total_rent_collected(),
            "pending": prop.total_rent_pending()
        })
    
    return Response(overview)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_insights(request):
    """
    Get current month's collection status with real-time updates
    """
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    properties = Property.objects.filter(owner=request.user)
    
    total_expected = 0
    for prop in properties:
        occupied_rooms = prop.rooms.filter(is_occupied=True)
        total_expected += sum(room.rent_amount for room in occupied_rooms)
    
    total_collected = Payment.objects.filter(
        property__owner=request.user,
        payment_date__month=current_month,
        payment_date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_pending = total_expected - total_collected
    overall_collection_percentage = (total_collected / total_expected * 100) if total_expected > 0 else 0
    
    total_payments_count = Payment.objects.filter(
        property__owner=request.user,
        payment_date__month=current_month,
        payment_date__year=current_year
    ).count()
    
    tenants_with_pending = Tenant.objects.filter(
        room__property__owner=request.user,
        is_active=True,
        rent_due_date__lte=now.date()
    ).exclude(
        payments__payment_date__month=current_month,
        payments__payment_date__year=current_year
    ).count()
    
    response_data = {
        "month": now.strftime("%B %Y"),
        "last_updated": now.isoformat(),
        "summary": {
            "total_expected_rent": float(total_expected),
            "total_collected": float(total_collected),
            "total_pending": float(total_pending),
            "collection_percentage": round(overall_collection_percentage, 2),
            "total_payments_received": total_payments_count,
            "tenants_with_pending_rent": tenants_with_pending
        }
    }
    
    return Response(response_data)
