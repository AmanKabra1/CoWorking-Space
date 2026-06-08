from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'status', 'employee_count', 'created_at']
    list_filter = ['status', 'city', 'state']
    search_fields = ['name', 'email', 'gst_number', 'pan_number']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {'fields': ('id', 'name', 'slug', 'status')}),
        ('Contact', {'fields': ('email', 'phone', 'website')}),
        ('Address', {'fields': ('address', 'city', 'state', 'pincode')}),
        ('Tax Info', {'fields': ('gst_number', 'pan_number')}),
        ('Contract', {'fields': ('contract_start', 'contract_end')}),
        ('Media & Notes', {'fields': ('logo', 'notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
