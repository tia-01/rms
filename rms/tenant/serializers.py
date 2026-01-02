from rest_framework import serializers
from .models import Tenant, Payment

class TenantSerializer(serializers.ModelSerializer):
    room_no = serializers.CharField(write_only=True)
    room_id = serializers.ReadOnlyField(source='room.id')
    room_number = serializers.ReadOnlyField(source='room.room_no')
    
    class Meta:
        model = Tenant
        fields = ['id', 'room_no', 'room_id', 'room_number', 'tenant_name', 'phone_no', 'email', 'rent_due_date', 'is_active']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        from property.models import Room
        room_no = validated_data.pop('room_no')
        try:
            room = Room.objects.get(room_no=room_no)
        except Room.DoesNotExist:
            raise serializers.ValidationError({"room_no": f"Room with number {room_no} does not exist."})
        
        if hasattr(room, 'tenant'):
            raise serializers.ValidationError({"room_no": "This room is already occupied."})
        
        tenant = Tenant.objects.create(room=room, **validated_data, is_active = True)
        room.is_occupied = True
        room.save()
        return tenant


class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.ReadOnlyField(source='tenant.tenant_name')
    room_no = serializers.ReadOnlyField(source='room.room_no')
    property_name = serializers.ReadOnlyField(source='property.name')
    
    class Meta:
        model = Payment
        fields = ['id', 'tenant', 'tenant_name', 'room', 'room_no', 
                  'property', 'property_name', 'amount', 'method', 'payment_date']
        read_only_fields = ['id', 'payment_date']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments using names instead of IDs"""
    tenant_name = serializers.CharField(write_only=True)
    room_no = serializers.CharField(write_only=True)
    property_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['tenant_name', 'room_no', 'property_name', 'amount', 'method']
    
    def validate(self, attrs):
        from property.models import Property, Room
        
        try:
            property_obj = Property.objects.get(name=attrs['property_name'])
        except Property.DoesNotExist:
            raise serializers.ValidationError({
                "property_name": f"Property '{attrs['property_name']}' does not exist."
            })
        
        try:
            room = Room.objects.get(room_no=attrs['room_no'], property=property_obj)
        except Room.DoesNotExist:
            raise serializers.ValidationError({
                "room_no": f"Room '{attrs['room_no']}' does not exist in property '{attrs['property_name']}'."
            })
        
        try:
            tenant = Tenant.objects.get(tenant_name=attrs['tenant_name'])
        except Tenant.DoesNotExist:
            raise serializers.ValidationError({
                "tenant_name": f"Tenant '{attrs['tenant_name']}' does not exist."
            })
        except Tenant.MultipleObjectsReturned:
            raise serializers.ValidationError({
                "tenant_name": f"Multiple tenants found with name '{attrs['tenant_name']}'. Please use a more specific identifier."
            })
        
        if tenant.room != room:
            raise serializers.ValidationError({
                "tenant_name": f"Tenant '{attrs['tenant_name']}' is not assigned to room '{attrs['room_no']}'."
            })
        
        attrs['tenant_obj'] = tenant
        attrs['room_obj'] = room
        attrs['property_obj'] = property_obj
        
        return attrs
    
    def create(self, validated_data):
        tenant_obj = validated_data.pop('tenant_obj')
        room_obj = validated_data.pop('room_obj')
        property_obj = validated_data.pop('property_obj')
        validated_data.pop('tenant_name')
        validated_data.pop('room_no')
        validated_data.pop('property_name')
        
        payment = Payment.objects.create(
            tenant=tenant_obj,
            room=room_obj,
            property=property_obj,
            **validated_data
        )
        return payment