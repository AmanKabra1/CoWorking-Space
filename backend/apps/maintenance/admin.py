from django.contrib import admin
from .models import MaintenanceTicket


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'title', 'company', 'category', 'priority',
        'status', 'assigned_to', 'resolved_at', 'created_at',
    ]
    list_filter = ['status', 'priority', 'category']
    search_fields = ['ticket_number', 'title', 'company__name']
    readonly_fields = ['ticket_number', 'reported_by', 'resolved_at', 'created_at', 'updated_at']
    raw_id_fields = ['assigned_to']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'building', 'reported_by', 'assigned_to'
        )
