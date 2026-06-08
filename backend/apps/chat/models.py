from django.db import models
from apps.core.models import TimeStampedModel


class ChatRoom(TimeStampedModel):
    COMPANY_GENERAL = 'company_general'
    DIRECT = 'direct'
    ROOM_TYPES = [
        (COMPANY_GENERAL, 'Company General'),
        (DIRECT, 'Direct Message'),
    ]

    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default=COMPANY_GENERAL)
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE, related_name='chat_rooms'
    )
    participants = models.ManyToManyField(
        'accounts.User', related_name='chat_rooms', blank=True
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.company})"


class ChatMessage(TimeStampedModel):
    TEXT = 'text'
    SYSTEM = 'system'
    MESSAGE_TYPES = [
        (TEXT, 'Text'),
        (SYSTEM, 'System'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='sent_messages'
    )
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default=TEXT)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} → {self.room}: {self.content[:40]}"
