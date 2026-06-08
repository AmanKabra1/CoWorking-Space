from django.db import models
from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (SUSPENDED, 'Suspended'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=15, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'companies_company'
        verbose_name_plural = 'companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        return self.employees.filter(is_active=True).count()
