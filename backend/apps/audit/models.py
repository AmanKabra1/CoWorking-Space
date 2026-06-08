from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.companies.models import Company

ACTION_CHOICES = [
    ('user_login', 'User Login'),
    ('user_logout', 'User Logout'),
    ('user_created', 'User Created'),
    ('user_updated', 'User Updated'),
    ('booking_created', 'Booking Created'),
    ('booking_approved', 'Booking Approved'),
    ('booking_rejected', 'Booking Rejected'),
    ('booking_cancelled', 'Booking Cancelled'),
    ('booking_completed', 'Booking Completed'),
    ('invoice_created', 'Invoice Created'),
    ('invoice_sent', 'Invoice Sent'),
    ('payment_recorded', 'Payment Recorded'),
    ('document_uploaded', 'Document Uploaded'),
    ('maintenance_created', 'Maintenance Ticket Created'),
    ('maintenance_assigned', 'Maintenance Ticket Assigned'),
    ('maintenance_resolved', 'Maintenance Ticket Resolved'),
    ('company_created', 'Company Created'),
    ('company_status_changed', 'Company Status Changed'),
    ('visitor_checked_in', 'Visitor Checked In'),
    ('visitor_checked_out', 'Visitor Checked Out'),
    ('application_submitted', 'Incubation Application Submitted'),
    ('application_accepted', 'Incubation Application Accepted'),
    ('application_rejected', 'Incubation Application Rejected'),
    ('system', 'System Action'),
]


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs',
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=50, blank=True, db_index=True)
    resource_id = models.UUIDField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        actor = self.user.email if self.user else 'system'
        return f"[{self.action}] {actor} — {self.description[:60]}"
