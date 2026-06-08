from django.contrib import admin
from .models import Facility, FacilityImage


class FacilityImageInline(admin.TabularInline):
    model = FacilityImage
    extra = 0
    fields = ['image', 'caption', 'is_primary', 'order']
    readonly_fields = ['id']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_type', 'building', 'floor', 'capacity', 'price_per_hour', 'price_per_day', 'is_active']
    list_filter = ['facility_type', 'building', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [FacilityImageInline]

    fieldsets = (
        (None, {'fields': ('id', 'name', 'facility_type', 'is_active')}),
        ('Location', {'fields': ('building', 'floor')}),
        ('Pricing', {'fields': ('capacity', 'price_per_hour', 'price_per_day')}),
        ('Details', {'fields': ('description', 'amenities', 'booking_rules')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
