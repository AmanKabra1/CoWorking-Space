from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'company', 'resource_type', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type']
    search_fields = ['description', 'user__email', 'company__name']
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
