from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.companies.models import Company

DOCUMENT_TYPE_CHOICES = [
    ('contract', 'Contract'),
    ('lease_agreement', 'Lease Agreement'),
    ('invoice', 'Invoice'),
    ('pitch_deck', 'Pitch Deck'),
    ('meeting_notes', 'Meeting Notes'),
    ('nda', 'NDA'),
    ('policy', 'Policy Document'),
    ('id_proof', 'ID / KYC Proof'),
    ('agreement', 'Agreement'),
    ('other', 'Other'),
]


def version_upload_path(instance, filename):
    company_id = instance.document.company_id
    doc_id = instance.document_id
    return f"documents/{company_id}/{doc_id}/{filename}"


class Document(TimeStampedModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='documents',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    doc_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES, default='other')
    tags = models.JSONField(default=list, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, related_name='uploaded_documents',
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_doc_type_display()}] — {self.company.name}"

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()

    @property
    def version_count(self):
        return self.versions.count()


class DocumentVersion(TimeStampedModel):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to=version_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, related_name='document_versions',
    )
    change_notes = models.TextField(blank=True, help_text='What changed in this version')

    class Meta:
        unique_together = [['document', 'version_number']]
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"
