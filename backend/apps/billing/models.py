from decimal import Decimal
from django.db import models

from apps.core.models import TimeStampedModel


class Invoice(TimeStampedModel):
    # Status choices
    DRAFT = 'draft'
    SENT = 'sent'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SENT, 'Sent'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
        (CANCELLED, 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(
        'companies.Company', on_delete=models.PROTECT, related_name='invoices'
    )
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()

    # Line items stored as JSON list:
    # [{"description": "Desk D-101-A (dedicated)", "qty": 1, "rate": "15000.00", "amount": "15000.00"}, ...]
    line_items = models.JSONField(default=list)

    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    # GST: CGST + SGST for intra-state; IGST for inter-state
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.00'))   # %
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.00'))   # %
    igst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))   # %
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    due_date = models.DateField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-billing_period_start', 'invoice_number']

    def __str__(self):
        return f"{self.invoice_number} — {self.company.name}"

    def compute_totals(self):
        """Recalculate GST amounts and total from subtotal + rates."""
        self.cgst_amount = (self.subtotal * self.cgst_rate / 100).quantize(Decimal('0.01'))
        self.sgst_amount = (self.subtotal * self.sgst_rate / 100).quantize(Decimal('0.01'))
        self.igst_amount = (self.subtotal * self.igst_rate / 100).quantize(Decimal('0.01'))
        self.total_amount = self.subtotal + self.cgst_amount + self.sgst_amount + self.igst_amount

    @classmethod
    def generate_invoice_number(cls, period_start):
        """Generate sequential invoice number: INV-YYYY-MM-NNNN."""
        prefix = f"INV-{period_start.year}-{period_start.month:02d}-"
        last = (
            cls.objects.filter(invoice_number__startswith=prefix)
            .order_by('invoice_number')
            .last()
        )
        if last:
            seq = int(last.invoice_number.split('-')[-1]) + 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"


class Payment(TimeStampedModel):
    UPI = 'upi'
    BANK_TRANSFER = 'bank_transfer'
    CASH = 'cash'
    CHEQUE = 'cheque'
    NEFT = 'neft'
    METHOD_CHOICES = [
        (UPI, 'UPI'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (CASH, 'Cash'),
        (CHEQUE, 'Cheque'),
        (NEFT, 'NEFT/RTGS'),
    ]

    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    company = models.ForeignKey(
        'companies.Company', on_delete=models.PROTECT, related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    upi_ref = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='recorded_payments'
    )

    class Meta:
        ordering = ['-paid_at', '-created_at']

    def __str__(self):
        return f"{self.invoice.invoice_number} — Rs {self.amount} ({self.status})"
