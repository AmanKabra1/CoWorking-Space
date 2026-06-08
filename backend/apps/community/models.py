from django.db import models
from apps.core.models import TimeStampedModel


class Post(TimeStampedModel):
    ANNOUNCEMENT = 'announcement'
    GENERAL = 'general'
    POST_TYPES = [
        (ANNOUNCEMENT, 'Announcement'),
        (GENERAL, 'General'),
    ]
    COMPANY = 'company'
    PLATFORM = 'platform'
    VISIBILITY = [
        (COMPANY, 'Company'),
        (PLATFORM, 'Platform-wide'),
    ]

    post_type = models.CharField(max_length=20, choices=POST_TYPES, default=GENERAL)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='posts')
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE,
        related_name='posts', null=True, blank=True
    )
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default=COMPANY)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} on {self.post}: {self.content[:40]}"


class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='events')
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE,
        related_name='events', null=True, blank=True
    )
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

    @property
    def rsvp_count(self):
        return self.rsvps.filter(status=EventRSVP.ATTENDING).count()


class EventRSVP(TimeStampedModel):
    ATTENDING = 'attending'
    MAYBE = 'maybe'
    DECLINED = 'declined'
    STATUS_CHOICES = [
        (ATTENDING, 'Attending'),
        (MAYBE, 'Maybe'),
        (DECLINED, 'Declined'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ATTENDING)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} → {self.event}: {self.status}"
