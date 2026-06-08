from django.contrib import admin
from .models import VisitorPass


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = [
        'pass_code', 'visitor_name', 'company', 'host', 'building',
        'status', 'scheduled_date', 'checked_in_at', 'checked_out_at',
    ]
    list_filter = ['status', 'scheduled_date']
    search_fields = ['visitor_name', 'visitor_email', 'pass_code', 'company__name']
    readonly_fields = ['pass_code', 'checked_in_at', 'checked_out_at', 'created_by', 'created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'host', 'building', 'created_by'
        )
