import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    SUPER_ADMIN = 'super_admin'
    COMPANY_ADMIN = 'company_admin'
    EMPLOYEE = 'employee'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (COMPANY_ADMIN, 'Company Admin'),
        (EMPLOYEE, 'Employee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)
    company = models.ForeignKey(
        'companies.Company',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees',
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    # ── Role helpers ──────────────────────────────────────
    @property
    def is_super_admin(self):
        return self.role == self.SUPER_ADMIN

    @property
    def is_company_admin(self):
        return self.role == self.COMPANY_ADMIN

    @property
    def is_employee_role(self):
        return self.role == self.EMPLOYEE
