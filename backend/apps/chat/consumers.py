import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = user

        room = await self.get_room()
        if not room:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_recent_messages()
        await self.send(text_data=json.dumps({'type': 'history', 'messages': messages}))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = data.get('content', '').strip()
            if not content:
                return
            message = await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'chat_message', 'message': message}
            )
        except (json.JSONDecodeError, KeyError):
            pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type': 'message', 'message': event['message']}))

    @database_sync_to_async
    def get_room(self):
        from apps.chat.models import ChatRoom
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if self.user.role == 'super_admin':
                return room
            if room.company_id == self.user.company_id:
                return room
            return None
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_recent_messages(self):
        from apps.chat.models import ChatMessage
        msgs = list(
            ChatMessage.objects.filter(room_id=self.room_id, is_deleted=False)
            .select_related('sender')
            .order_by('-created_at')[:50]
        )
        return [self._serialize(m) for m in reversed(msgs)]

    @database_sync_to_async
    def save_message(self, content):
        from apps.chat.models import ChatMessage
        m = ChatMessage.objects.create(room_id=self.room_id, sender=self.user, content=content)
        return self._serialize(m)

    @staticmethod
    def _serialize(m):
        return {
            'id': str(m.id),
            'content': m.content,
            'sender_id': str(m.sender_id) if m.sender_id else None,
            'sender_name': (m.sender.get_full_name() or m.sender.email) if m.sender else 'System',
            'created_at': m.created_at.isoformat(),
        }
