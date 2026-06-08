from rest_framework import serializers
from apps.chat.models import ChatRoom, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'content', 'message_type', 'is_deleted', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_name', 'is_deleted', 'created_at']

    def get_sender_name(self, obj):
        if obj.sender:
            return obj.sender.get_full_name() or obj.sender.email
        return 'System'


class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'company', 'company_name', 'last_message', 'updated_at']
        read_only_fields = ['id', 'company', 'company_name', 'last_message', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.filter(is_deleted=False).last()
        if msg:
            return {'content': msg.content[:80], 'created_at': msg.created_at.isoformat()}
        return None
