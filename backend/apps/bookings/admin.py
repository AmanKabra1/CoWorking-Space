from django.contrib import admin
from django.utils import timezone
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'facility', 'company', 'booked_by', 'booking_date',
        'start_time', 'end_time', 'duration_hours', 'status', 'total_amount',
    ]
    list_filter = ['status', 'facility__facility_type', 'booking_date', 'company']
    search_fields = ['facility__name', 'company__name', 'booked_by__email', 'purpose']
    readonly_fields = ['id', 'duration_hours', 'total_amount', 'approved_by', 'approved_at', 'created_at', 'updated_at']
    ordering = ['-booking_date', 'start_time']

    fieldsets = (
        (None, {'fields': ('id', 'facility', 'company', 'booked_by', 'status')}),
        ('Schedule', {'fields': ('booking_date', 'start_time', 'end_time', 'duration_hours')}),
        ('Details', {'fields': ('purpose', 'attendees_count', 'total_amount')}),
        ('Approval', {'fields': ('approved_by', 'approved_at', 'rejection_reason')}),
        ('Internal Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    actions = ['approve_bookings', 'reject_bookings']

    @admin.action(description='Approve selected bookings')
    def approve_bookings(self, request, queryset):
        updated = queryset.filter(status=Booking.PENDING).update(
            status=Booking.APPROVED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )
        self.message_user(request, f'{updated} booking(s) approved.')

    @admin.action(description='Reject selected bookings')
    def reject_bookings(self, request, queryset):
        updated = queryset.filter(status=Booking.PENDING).update(status=Booking.REJECTED)
        self.message_user(request, f'{updated} booking(s) rejected.')
