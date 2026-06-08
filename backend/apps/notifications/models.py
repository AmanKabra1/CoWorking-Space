from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

NOTIFICATION_TYPE_CHOICES = [
    ('booking_approved', 'Booking Approved'),
    ('booking_rejected', 'Booking Rejected'),
    ('booking_cancelled', 'Booking Cancelled'),
    ('invoice_sent', 'Invoice Sent'),
    ('invoice_overdue', 'Invoice Overdue'),
    ('invoice_paid', 'Invoice Paid'),
    ('maintenance_assigned', 'Maintenance Assigned'),
    ('maintenance_resolved', 'Maintenance Resolved'),
    ('visitor_arrival', 'Visitor Arrival'),
    ('system', 'System'),
]


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPE_CHOICES, default='system',
    )
    is_read = models.BooleanField(default=False)
    related_id = models.UUIDField(null=True, blank=True)
    related_type = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user.email}"

    @classmethod
    def create_for_user(cls, user, title, message, notification_type,
                        related_id=None, related_type=''):
        return cls.objects.create(
            user=user, title=title, message=message,
            notification_type=notification_type,
            related_id=related_id, related_type=related_type,
        )

    @classmethod
    def create_for_company(cls, company, title, message, notification_type,
                           related_id=None, related_type='', exclude_user=None):
        users = company.employees.all()
        if exclude_user:
            users = users.exclude(pk=exclude_user.pk)
        notifications = [
            cls(
                user=user, title=title, message=message,
                notification_type=notification_type,
                related_id=related_id, related_type=related_type,
            )
            for user in users
        ]
        cls.objects.bulk_create(notifications)
