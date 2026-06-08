from rest_framework import serializers
from .models import AIConversation


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, help_text='User message to the AI assistant')
    session_id = serializers.UUIDField(
        required=False, allow_null=True,
        help_text='Continue an existing conversation (omit to start new)',
    )


class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    reply = serializers.CharField()
    model = serializers.CharField()


class BookingSuggestionSerializer(serializers.Serializer):
    facility_id = serializers.UUIDField(help_text='Facility UUID')
    date = serializers.DateField(help_text='Date to find slots for (YYYY-MM-DD)')


class InsightsSerializer(serializers.Serializer):
    INSIGHT_TYPES = [
        ('bookings', 'Booking Analytics'),
        ('invoices', 'Invoice & Revenue'),
        ('facilities', 'Facility Usage'),
    ]
    insight_type = serializers.ChoiceField(choices=INSIGHT_TYPES)
    date_from = serializers.DateField(required=False, help_text='Start of analysis period')
    date_to = serializers.DateField(required=False, help_text='End of analysis period')


class SmartSearchSerializer(serializers.Serializer):
    RESOURCE_TYPES = [
        ('bookings', 'Bookings'),
        ('invoices', 'Invoices'),
        ('facilities', 'Facilities'),
    ]
    query = serializers.CharField(max_length=500, help_text='Natural language search query')
    resource = serializers.ChoiceField(choices=RESOURCE_TYPES, help_text='What to search in')


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ['id', 'session_type', 'messages', 'model_used', 'total_tokens', 'created_at', 'updated_at']
        read_only_fields = fields
