from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel


class SeatLease(TimeStampedModel):
    """
    A company sub-leasing one of its assigned desks to an outside tenant.
    e.g. a 30-person company opens its spare seats to freelancers/other teams.
    """

    ACTIVE = 'active'
    ENDED = 'ended'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (ENDED, 'Ended'),
    ]

    desk = models.ForeignKey(
        'workspace.Desk', on_delete=models.PROTECT, related_name='seat_leases'
    )
    # The company subleasing the desk out (must own/lease the desk).
    lessor_company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE, related_name='seat_leases'
    )

    # Sub-tenant details (no account required).
    lessee_name = models.CharField(max_length=150)
    lessee_email = models.EmailField(blank=True)
    lessee_phone = models.CharField(max_length=15, blank=True)
    lessee_company = models.CharField(max_length=200, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'subleasing_seatlease'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.desk.desk_code} → {self.lessee_name} ({self.get_status_display()})'
