import secrets
import string

from django.db import models
from apps.core.models import TimeStampedModel

# Unambiguous alphabet for join codes (no O/0, I/1) — easy to read & type.
_JOIN_CODE_ALPHABET = ''.join(
    c for c in (string.ascii_uppercase + string.digits) if c not in 'O0I1'
)


def generate_join_code(length=8):
    return ''.join(secrets.choice(_JOIN_CODE_ALPHABET) for _ in range(length))


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
    # Employees self-register against this code (see public /auth/join/ endpoint).
    join_code = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        help_text='Share with employees so they can self-register into this company.',
    )

    class Meta:
        db_table = 'companies_company'
        verbose_name_plural = 'companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = self.new_unique_join_code()
        super().save(*args, **kwargs)

    @classmethod
    def new_unique_join_code(cls):
        """A join code guaranteed not to collide with an existing company."""
        for _ in range(20):
            code = generate_join_code()
            if not cls.objects.filter(join_code=code).exists():
                return code
        # Astronomically unlikely; widen the space as a last resort.
        return generate_join_code(12)

    @property
    def employee_count(self):
        return self.employees.filter(is_active=True).count()

    def leases_building(self, building):
        """
        True if this company occupies space in the given building —
        i.e. it has at least one assigned desk or parking slot there.
        Used to decide whether a facility booking is internal (free,
        approved by company admin) or external (paid, approved by super admin).
        """
        from apps.workspace.models import Desk, ParkingSlot
        has_desk = Desk.objects.filter(
            company=self, room__floor__building=building
        ).exists()
        if has_desk:
            return True
        return ParkingSlot.objects.filter(company=self, building=building).exists()
