from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.companies.models import Company
from apps.workspace.models import Building

CATEGORY_CHOICES = [
    ('electrical', 'Electrical'),
    ('plumbing', 'Plumbing'),
    ('hvac', 'HVAC / Air Conditioning'),
    ('internet', 'Internet / Network'),
    ('furniture', 'Furniture'),
    ('cleaning', 'Cleaning'),
    ('security', 'Security'),
    ('elevator', 'Elevator'),
    ('other', 'Other'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class MaintenanceTicket(TimeStampedModel):
    OPEN = 'open'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (ASSIGNED, 'Assigned'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED, 'Resolved'),
        (CLOSED, 'Closed'),
    ]

    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='maintenance_tickets')
    building = models.ForeignKey(
        Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_tickets',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=OPEN)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, related_name='reported_tickets',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets',
    )
    image = models.ImageField(upload_to='maintenance/', null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number} — {self.title} [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._next_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _next_ticket_number():
        year = timezone.now().year
        count = MaintenanceTicket.objects.filter(created_at__year=year).count() + 1
        return f"TKT-{year}-{count:04d}"
