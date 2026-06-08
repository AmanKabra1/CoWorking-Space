import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class SignatureRequest(TimeStampedModel):
    DRAFT = 'draft'
    PENDING = 'pending'
    PARTIALLY_SIGNED = 'partially_signed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending'),
        (PARTIALLY_SIGNED, 'Partially Signed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED, 'Expired'),
    ]

    title = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='esign/requests/%Y/%m/')
    message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='signature_requests_created'
    )
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE, related_name='signature_requests'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    expires_at = models.DateTimeField(null=True, blank=True)
    certificate_file = models.FileField(
        upload_to='esign/certificates/%Y/%m/', null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.status}]"

    def _refresh_status(self):
        records = list(self.records.all())
        if not records:
            return
        signed = [r for r in records if r.status == SignatureRecord.SIGNED]
        if len(signed) == len(records):
            self.status = self.COMPLETED
        elif signed:
            self.status = self.PARTIALLY_SIGNED
        else:
            self.status = self.PENDING
        self.save(update_fields=['status', 'updated_at'])


class SignatureRecord(TimeStampedModel):
    PENDING = 'pending'
    SIGNED = 'signed'
    DECLINED = 'declined'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SIGNED, 'Signed'),
        (DECLINED, 'Declined'),
    ]

    request = models.ForeignKey(SignatureRequest, on_delete=models.CASCADE, related_name='records')
    signer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='signature_records'
    )
    signer_email = models.EmailField()
    signer_name = models.CharField(max_length=150)
    signing_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_data = models.TextField(blank=True, help_text='Base64 signature image or typed name')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ('request', 'signer_email')

    def __str__(self):
        return f"{self.signer_name} ({self.signer_email}) — {self.status}"
