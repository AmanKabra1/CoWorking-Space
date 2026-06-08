from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.companies.models import Company

INDUSTRY_CHOICES = [
    ('fintech', 'Fintech'),
    ('edtech', 'Edtech'),
    ('healthtech', 'Healthtech'),
    ('agritech', 'Agritech'),
    ('saas', 'SaaS'),
    ('ecommerce', 'E-Commerce'),
    ('logistics', 'Logistics & Supply Chain'),
    ('cleantech', 'Cleantech'),
    ('ai_ml', 'AI / ML'),
    ('iot', 'IoT'),
    ('other', 'Other'),
]

STAGE_CHOICES = [
    ('idea', 'Idea Stage'),
    ('mvp', 'MVP'),
    ('early_traction', 'Early Traction'),
    ('growth', 'Growth'),
    ('scale', 'Scale'),
]

FUNDING_TYPE_CHOICES = [
    ('grant', 'Grant'),
    ('pre_seed', 'Pre-Seed'),
    ('seed', 'Seed'),
    ('series_a', 'Series A'),
    ('series_b', 'Series B'),
    ('bridge', 'Bridge Round'),
    ('other', 'Other'),
]


class StartupProfile(TimeStampedModel):
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name='startup_profile',
    )
    startup_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    founded_date = models.DateField(null=True, blank=True)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='other')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='idea')
    team_size = models.PositiveIntegerField(default=1)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='incubation/logos/', null=True, blank=True)
    pitch_deck = models.FileField(upload_to='incubation/pitch_decks/', null=True, blank=True)
    business_plan = models.FileField(upload_to='incubation/business_plans/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.startup_name} ({self.company.name})"


class IncubationApplication(TimeStampedModel):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SUBMITTED, 'Submitted'),
        (UNDER_REVIEW, 'Under Review'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (WITHDRAWN, 'Withdrawn'),
    ]

    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, related_name='applications',
    )
    cohort = models.CharField(max_length=20, help_text='E.g. 2026-Q1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)

    problem_statement = models.TextField()
    solution = models.TextField()
    market_size = models.TextField(blank=True)
    traction = models.TextField(blank=True)
    funding_ask = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPE_CHOICES, blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_applications',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        unique_together = [['startup', 'cohort']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.startup.startup_name} — {self.cohort} [{self.status}]"


class ApplicationNote(TimeStampedModel):
    application = models.ForeignKey(
        IncubationApplication, on_delete=models.CASCADE, related_name='notes',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='incubation_notes',
    )
    content = models.TextField()
    is_internal = models.BooleanField(
        default=True,
        help_text='Internal notes are visible to Super Admins only',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.author.get_full_name()} on {self.application}"


class FundingRound(TimeStampedModel):
    PLANNING = 'planning'
    SEEKING = 'seeking'
    CLOSED = 'closed'

    STATUS_CHOICES = [
        (PLANNING, 'Planning'),
        (SEEKING, 'Seeking'),
        (CLOSED, 'Closed'),
    ]

    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, related_name='funding_rounds',
    )
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPE_CHOICES)
    amount_sought = models.DecimalField(max_digits=14, decimal_places=2)
    amount_raised = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PLANNING)
    target_date = models.DateField(null=True, blank=True)
    investors = models.TextField(blank=True, help_text='Comma-separated investor names')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.startup.startup_name} — {self.get_funding_type_display()} [{self.status}]"
