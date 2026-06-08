import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.companies.models import Company
from apps.workspace.models import Building


def _generate_pass_code():
    return uuid.uuid4().hex[:8].upper()


class VisitorPass(TimeStampedModel):
    SCHEDULED = 'scheduled'
    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (SCHEDULED, 'Scheduled'),
        (CHECKED_IN, 'Checked In'),
        (CHECKED_OUT, 'Checked Out'),
        (CANCELLED, 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='visitor_passes')
    visitor_name = models.CharField(max_length=200)
    visitor_email = models.EmailField(blank=True)
    visitor_phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=300)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='hosted_visitors',
    )
    building = models.ForeignKey(
        Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitor_passes',
    )
    pass_code = models.CharField(max_length=20, unique=True, default=_generate_pass_code)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=SCHEDULED)
    scheduled_date = models.DateField()
    valid_from = models.TimeField()
    valid_until = models.TimeField()
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, related_name='created_visitor_passes',
    )

    class Meta:
        ordering = ['-scheduled_date', '-created_at']

    def __str__(self):
        return f"{self.visitor_name} → {self.host.get_full_name()} [{self.pass_code}]"
