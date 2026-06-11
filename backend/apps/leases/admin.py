from django.contrib import admin
from .models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ['company', 'building', 'floor', 'seats_leased', 'start_date', 'end_date', 'monthly_rate', 'status']
    list_filter = ['status', 'building', 'start_date']
    search_fields = ['company__name', 'building__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
