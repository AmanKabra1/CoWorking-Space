from django.contrib import admin
from .models import SeatLease


@admin.register(SeatLease)
class SeatLeaseAdmin(admin.ModelAdmin):
    list_display = ['desk', 'lessor_company', 'lessee_name', 'start_date', 'end_date', 'monthly_rate', 'status']
    list_filter = ['status', 'lessor_company', 'start_date']
    search_fields = ['lessee_name', 'lessee_company', 'desk__desk_code']
    readonly_fields = ['id', 'created_at', 'updated_at']
