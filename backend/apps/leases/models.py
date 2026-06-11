from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel


class Lease(TimeStampedModel):
    """
    A lease agreement: a company rents a number of seats on a building/floor
    for a term. This is the contract that says e.g. "Company A leases Floor 1,
    100 seats" — the basis for seat-utilization (leased vs used vs sub-leased).
    """

    ACTIVE = 'active'
    EXPIRED = 'expired'
    TERMINATED = 'terminated'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (TERMINATED, 'Terminated'),
    ]

    company = models.ForeignKey(
        'companies.Company', on_delete=models.PROTECT, related_name='leases'
    )
    building = models.ForeignKey(
        'workspace.Building', on_delete=models.CASCADE, related_name='leases'
    )
    floor = models.ForeignKey(
        'workspace.Floor', on_delete=models.SET_NULL, null=True, blank=True, related_name='leases'
    )
    seats_leased = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    monthly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=ACTIVE)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'leases_lease'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.company.name} → {self.building.name} ({self.seats_leased} seats)'

    @property
    def seats_used(self):
        """Employees of the lessee company currently active."""
        return self.company.employees.filter(is_active=True).count()

    @property
    def seats_available(self):
        return max(self.seats_leased - self.seats_used, 0)
