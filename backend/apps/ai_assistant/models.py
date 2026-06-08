from django.db import models
from apps.core.models import TimeStampedModel


class AIConversation(TimeStampedModel):
    """Stores multi-turn chat sessions per user."""
    CHAT = 'chat'
    SEARCH = 'search'
    INSIGHTS = 'insights'
    SUGGESTIONS = 'suggestions'
    TYPE_CHOICES = [
        (CHAT, 'General Chat'),
        (SEARCH, 'Smart Search'),
        (INSIGHTS, 'Report Insights'),
        (SUGGESTIONS, 'Booking Suggestions'),
    ]

    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='ai_conversations'
    )
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE,
        null=True, blank=True, related_name='ai_conversations',
    )
    session_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=CHAT)
    # [{role: "user"|"model", parts: "..."}]
    messages = models.JSONField(default=list)
    total_tokens = models.PositiveIntegerField(default=0)
    model_used = models.CharField(max_length=60, default='gemini-1.5-flash')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.get_session_type_display()} ({self.created_at:%Y-%m-%d})'

    def add_message(self, role: str, content: str):
        self.messages.append({'role': role, 'content': content})

    def get_history_for_gemini(self):
        """Convert stored messages to Gemini API format."""
        return [
            {'role': m['role'], 'parts': [m['content']]}
            for m in self.messages[:-1]  # exclude last user message (sent separately)
        ]
