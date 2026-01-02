from rest_framework import viewsets, status
from .models import Tenant, Payment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from .serializers import TenantSerializer, PaymentSerializer, PaymentCreateSerializer
# Create your views here.

        
class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_payment_history(request, pk):
    """
    Get comprehensive payment history and financial summary for a specific tenant
    """
    try:
        tenant = Tenant.objects.get(pk=pk)
    except Tenant.DoesNotExist:
        return Response(
            {"error": "Tenant not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    payments = tenant.payments.all().order_by('-payment_date')
    
    tenant_info = {
        "tenant_id": tenant.id,
        "tenant_name": tenant.tenant_name,
        "phone_no": tenant.phone_no,
        "email": tenant.email,
        "room_no": tenant.room.room_no,
        "property_name": tenant.room.property.name,
        "monthly_rent": float(tenant.room.rent_amount),
        "rent_due_date": tenant.rent_due_date.isoformat(),
        "is_active": tenant.is_active,
        "lease_start_date": tenant.lease_start_date.isoformat() if tenant.lease_start_date else None,
        "lease_end_date": tenant.lease_end_date.isoformat() if tenant.lease_end_date else None,
    }
   
    financial_summary = {
        "is_rent_due": tenant.is_rent_due(), 
        "payment_history_summary": tenant.payment_history_summary(), 
    }
    
    payment_serializer = PaymentSerializer(payments, many=True)
   
    response_data = {
        "tenant_info": tenant_info,
        "financial_summary": financial_summary,
        "payment_history": payment_serializer.data,
        "generated_at": timezone.now().isoformat()
    }
    
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_payment_status(request):
    """
    Quick view of which tenants have paid and who owes rent for current month
    """
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    tenants = Tenant.objects.filter(
        room__property__owner=request.user,
        is_active=True
    ).select_related('room', 'room__property')
    
    paid_tenants = []
    pending_tenants = []
    
    for tenant in tenants:
        has_paid = Payment.objects.filter(
            tenant=tenant,
            payment_date__month=current_month,
            payment_date__year=current_year
        ).exists()
        
        amount_paid = Payment.objects.filter(
            tenant=tenant,
            payment_date__month=current_month,
            payment_date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        tenant_data = {
            "tenant_id": tenant.id,
            "tenant_name": tenant.tenant_name,
            "phone_no": tenant.phone_no,
            "email": tenant.email,
            "property_name": tenant.room.property.name,
            "room_no": tenant.room.room_no,
            "rent_amount": float(tenant.room.rent_amount),
            "rent_due_date": tenant.rent_due_date.isoformat(),
            "is_overdue": tenant.is_rent_due()
        }
        
        if has_paid:
            tenant_data["amount_paid"] = float(amount_paid)
            tenant_data["payment_status"] = "paid"
            paid_tenants.append(tenant_data)
        else:
            tenant_data["amount_due"] = float(tenant.room.rent_amount)
            tenant_data["payment_status"] = "pending"
            pending_tenants.append(tenant_data)
    
    response_data = {
        "month": now.strftime("%B %Y"),
        "last_updated": now.isoformat(),
        "summary": {
            "total_tenants": len(tenants),
            "paid_count": len(paid_tenants),
            "pending_count": len(pending_tenants)
        },
        "paid_tenants": paid_tenants,
        "pending_tenants": pending_tenants
    }
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_payment(request):
    """Log a new payment using tenant name, room number, and property name"""
    serializer = PaymentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payment = serializer.save()
    
    response_serializer = PaymentSerializer(payment)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_payments(request):
    """List all payments with optional filters"""
    payments = Payment.objects.all().select_related('tenant', 'room', 'property')
   
    tenant_name = request.query_params.get('tenant_name')
    if tenant_name:
        payments = payments.filter(tenant__tenant_name__icontains=tenant_name)
    
    property_name = request.query_params.get('property_name')
    if property_name:
        payments = payments.filter(property__name__icontains=property_name)
    
    room_no = request.query_params.get('room_no')
    if room_no:
        payments = payments.filter(room__room_no=room_no)
    
    method = request.query_params.get('method')
    if method:
        payments = payments.filter(method=method)
    
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_status(request):
    """
    Simple monitor showing all vacant and occupied rooms across all properties
    with tenant information for occupied rooms
    """
    from property.models import Property
    
    properties = Property.objects.all().prefetch_related('rooms', 'rooms__tenant')
    
    all_vacant_rooms = []
    all_occupied_rooms = []
    
    for property_obj in properties:
        for room in property_obj.rooms.all():
            
            if room.is_occupied and hasattr(room, 'tenant'):
                tenant = room.tenant
                all_occupied_rooms.append({
                    "property_name": property_obj.name,
                    "room_no": room.room_no,
                    "rent_amount": float(room.rent_amount),
                    "tenant_name": tenant.tenant_name,
                    "tenant_phone": tenant.phone_no,
                    "tenant_email": tenant.email,
                    "lease_start": tenant.lease_start_date.isoformat() if tenant.lease_start_date else None,
                    "rent_due_date": tenant.rent_due_date.isoformat(),
                    "is_active": tenant.is_active,
                    "is_rent_overdue": tenant.is_rent_due()
                })
            else:
                all_vacant_rooms.append({
                    "property_name": property_obj.name,
                    "room_no": room.room_no,
                    "rent_amount": float(room.rent_amount)
                })
    
    return Response({
        "summary": {
            "total_rooms": len(all_vacant_rooms) + len(all_occupied_rooms),
            "occupied": len(all_occupied_rooms),
            "vacant": len(all_vacant_rooms)
        },
        "vacant_rooms": all_vacant_rooms,
        "occupied_rooms": all_occupied_rooms
    })