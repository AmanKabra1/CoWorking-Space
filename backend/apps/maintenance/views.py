from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsSuperAdmin, IsSuperAdminOrCompanyAdmin
from .models import MaintenanceTicket
from .serializers import MaintenanceTicketSerializer, AssignTicketSerializer, ResolveTicketSerializer


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceTicketSerializer
    search_fields = ['title', 'description', 'ticket_number']
    filterset_fields = ['status', 'priority', 'category', 'building']
    ordering_fields = ['priority', 'status', 'created_at', 'resolved_at']

    def get_queryset(self):
        user = self.request.user
        qs = MaintenanceTicket.objects.select_related(
            'company', 'building', 'reported_by', 'assigned_to'
        )
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['assign', 'close']:
            return [IsSuperAdmin()]
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'start', 'resolve']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status not in [MaintenanceTicket.OPEN, MaintenanceTicket.ASSIGNED]:
            return Response(
                {'detail': 'Only open or assigned tickets can be reassigned.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = AssignTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            assignee = User.objects.get(pk=ser.validated_data['assigned_to'])
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        ticket.assigned_to = assignee
        ticket.status = MaintenanceTicket.ASSIGNED
        ticket.save(update_fields=['assigned_to', 'status', 'updated_at'])

        from apps.notifications.tasks import notify_ticket_assigned
        notify_ticket_assigned.delay(str(ticket.pk))

        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != MaintenanceTicket.ASSIGNED:
            return Response(
                {'detail': 'Only assigned tickets can be started.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket.status = MaintenanceTicket.IN_PROGRESS
        ticket.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status not in [MaintenanceTicket.ASSIGNED, MaintenanceTicket.IN_PROGRESS]:
            return Response(
                {'detail': 'Only assigned or in-progress tickets can be resolved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ResolveTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ticket.status = MaintenanceTicket.RESOLVED
        ticket.resolution_notes = ser.validated_data['resolution_notes']
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=['status', 'resolution_notes', 'resolved_at', 'updated_at'])

        from apps.notifications.tasks import notify_ticket_resolved
        notify_ticket_resolved.delay(str(ticket.pk))

        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != MaintenanceTicket.RESOLVED:
            return Response(
                {'detail': 'Only resolved tickets can be closed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket.status = MaintenanceTicket.CLOSED
        ticket.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(ticket).data)
