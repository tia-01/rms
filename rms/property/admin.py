from django.contrib import admin
from .models import Property, Room
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Register your models here.

# admin.site.register(Property)
# admin.site.register(Room)
# admin.site.register(Tenant)

class PropertyResource(resources.ModelResource):

    class Meta:
        model = Property
        
class RoomResource(resources.ModelResource):
    class Meta:
        model = Room

        
        
@admin.register(Property)
class PropertyAdmin(ImportExportModelAdmin):
    resource_class = PropertyResource
    list_display = ('name', 'address', 'price')
    search_fields = ('name', 'address')

@admin.register(Room)
class RoomAdmin(ImportExportModelAdmin):
    resource_class = RoomResource
    list_display = ('room_no', 'property', 'rent_amount', 'is_occupied')
    list_filter = ('property', 'is_occupied')
    search_fields = ('room_no', 'property__name')
    