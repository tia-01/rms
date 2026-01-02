from rest_framework import serializers
from .models import Property, Room

class RoomSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'property', 'property_name', 'room_no', 'rent_amount', 'is_occupied', 'tenant_name']
        read_only_fields = ['id', 'is_occupied']
    
    def get_property_name(self, obj):
        return obj.property.name if obj.property else None
    
    def get_tenant_name(self, obj):
        return obj.tenant.tenant_name if hasattr(obj, 'tenant') else None


class PropertySerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['owner']


