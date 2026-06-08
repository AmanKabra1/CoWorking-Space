from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.chat.models import ChatRoom, ChatMessage
from apps.chat.serializers import ChatRoomSerializer, ChatMessageSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return ChatRoom.objects.all().select_related('company')
        return ChatRoom.objects.filter(company=user.company).select_related('company')

    @action(detail=False, methods=['get', 'post'], url_path='company-general')
    def company_general(self, request):
        """Get or create the general chat room for the user's company."""
        company = request.user.company
        if not company:
            return Response({'detail': 'No company associated.'}, status=400)
        room, _ = ChatRoom.objects.get_or_create(
            company=company,
            room_type=ChatRoom.COMPANY_GENERAL,
            defaults={'name': f"{company.name} — General"},
        )
        return Response(ChatRoomSerializer(room).data)


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        room_id = self.kwargs.get('room_pk') or self.request.query_params.get('room')
        user = self.request.user
        qs = ChatMessage.objects.filter(is_deleted=False).select_related('sender', 'room')
        if room_id:
            qs = qs.filter(room_id=room_id)
        if not user.is_super_admin:
            qs = qs.filter(room__company=user.company)
        return qs.order_by('-created_at')
