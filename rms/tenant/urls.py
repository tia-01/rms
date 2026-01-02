from django.urls import path, include
from rest_framework import routers
from .views import TenantViewSet, log_payment, list_payments, tenant_payment_status, tenant_payment_history, room_status

router = routers.DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    path('', include(router.urls)),
    path('log-payment/', log_payment, name='log-payment'),
    path('payments/', list_payments, name='list_payments'),
    path('tenant-payment-status/', tenant_payment_status, name='tenant-payment-status'),
    path('<int:pk>/payment-history/', tenant_payment_history, name='tenant_payment_history'),
    path('room-status/', room_status, name='room-status'),
]
