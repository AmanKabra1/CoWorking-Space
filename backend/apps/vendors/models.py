from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel


class Vendor(TimeStampedModel):
    """
    A supplier / service provider billed by the operator —
    utilities, catering, cleaning, maintenance, supplies, etc.
    """

    UTILITIES = 'utilities'
    CATERING = 'catering'
    CLEANING = 'cleaning'
    MAINTENANCE = 'maintenance'
    SUPPLIES = 'supplies'
    SECURITY = 'security'
    INTERNET = 'internet'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (UTILITIES, 'Utilities (Electricity / Water)'),
        (CATERING, 'Catering / Pantry'),
        (CLEANING, 'Cleaning / Housekeeping'),
        (MAINTENANCE, 'Maintenance / Repairs'),
        (SUPPLIES, 'Supplies'),
        (SECURITY, 'Security'),
        (INTERNET, 'Internet / Telecom'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=OTHER)
    building = models.ForeignKey(
        'workspace.Building', on_delete=models.CASCADE,
        related_name='vendors', null=True, blank=True,
        help_text='Optional — leave blank for an operator-wide vendor.',
    )
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendors_vendor'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_category_display()})'


class VendorBill(TimeStampedModel):
    """A bill / expense raised by a vendor against a building."""

    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
        (CANCELLED, 'Cancelled'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills')
    building = models.ForeignKey(
        'workspace.Building', on_delete=models.CASCADE, related_name='vendor_bills'
    )
    bill_number = models.CharField(max_length=50)
    bill_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to='vendor_bills/', null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'vendors_vendorbill'
        ordering = ['-bill_date', 'bill_number']

    def __str__(self):
        return f'{self.bill_number} — {self.vendor.name} ({self.total_amount})'

    def compute_total(self):
        self.total_amount = (self.amount or Decimal('0.00')) + (self.tax_amount or Decimal('0.00'))
