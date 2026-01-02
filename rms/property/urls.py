from django.urls import path, include
from rest_framework import routers
from .views import PropertyViewSet, RoomViewSet
from .views import send_due_rent_view, housewise_overview, monthly_insights

router = routers.DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'rooms', RoomViewSet, basename='room')
# router.register(r'rent-due-sms', RentDueSMSAPIView, basename='rent-due-sms')

urlpatterns = [
    path('', include(router.urls)),
    path('send-due-rent/', send_due_rent_view, name='send-due-rent'),
    path('housewise-overview/', housewise_overview, name='housewise-overview'),
    path('monthly-insights/', monthly_insights, name='monthly-insights'),
]
