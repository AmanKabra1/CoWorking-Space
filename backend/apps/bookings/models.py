from decimal import Decimal
from datetime import datetime
from django.db import models
from apps.core.models import TimeStampedModel


class Booking(TimeStampedModel):
    PENDING = 'pending'
    APPROVED = 'approved'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending Approval'),
        (APPROVED, 'Approved — awaiting payment'),
        (CONFIRMED, 'Confirmed — paid'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    ]

    INTERNAL = 'internal'
    EXTERNAL = 'external'

    BOOKING_TYPE_CHOICES = [
        (INTERNAL, 'Internal — booker leases this building'),
        (EXTERNAL, 'External — booker does not lease this building'),
    ]

    facility = models.ForeignKey(
        'facilities.Facility', on_delete=models.PROTECT, related_name='bookings'
    )
    # company/booked_by are null for public (guest) bookings made without login.
    company = models.ForeignKey(
        'companies.Company', on_delete=models.PROTECT, related_name='bookings',
        null=True, blank=True,
    )
    booked_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='bookings',
        null=True, blank=True,
    )

    # Guest contact details — filled for public bookings (no user account).
    guest_name = models.CharField(max_length=150, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=15, blank=True)
    guest_company = models.CharField(max_length=200, blank=True)

    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    booking_type = models.CharField(
        max_length=10, choices=BOOKING_TYPE_CHOICES, default=EXTERNAL,
        help_text='Set automatically: internal if the company leases the building, else external.',
    )
    payment_required = models.BooleanField(
        default=True,
        help_text='False for internal bookings (included in lease); True for external (paid).',
    )
    purpose = models.TextField()
    attendees_count = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Approval
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_bookings',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Internal (Super Admin only)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'bookings_booking'
        ordering = ['-booking_date', 'start_time']

    def __str__(self):
        return (
            f'{self.facility.name} | {self.company.name} | '
            f'{self.booking_date} {self.start_time}–{self.end_time}'
        )

    def calculate_duration(self):
        start = datetime.combine(datetime.min.date(), self.start_time)
        end = datetime.combine(datetime.min.date(), self.end_time)
        return Decimal(str(round((end - start).total_seconds() / 3600, 2)))

    def calculate_amount(self):
        duration = self.calculate_duration()
        if duration >= 8:
            return self.facility.price_per_day
        return (self.facility.price_per_hour * duration).quantize(Decimal('0.01'))
