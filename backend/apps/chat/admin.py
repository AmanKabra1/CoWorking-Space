from django.contrib import admin
from apps.chat.models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'company', 'updated_at']
    list_filter = ['room_type', 'company']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'is_deleted']
    search_fields = ['content', 'sender__email']
