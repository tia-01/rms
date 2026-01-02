from django.contrib import admin
from .models import Tenant, Payment
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Register your models here.

# admin.site.register(Tenant)

class TenantResource(resources.ModelResource):
    class Meta:
        model = Tenant
        
class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment

@admin.register(Tenant)
class TenantAdmin(ImportExportModelAdmin):
    resource_class = TenantResource
    list_display = ('tenant_name', 'room', 'phone_no', 'rent_due_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('tenant_name', 'phone_no')

admin.site.register(Payment)
