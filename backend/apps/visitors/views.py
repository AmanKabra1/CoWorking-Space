from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from .models import VisitorPass
from .serializers import VisitorPassSerializer, VisitorPassPublicSerializer


class VisitorPassViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorPassSerializer
    search_fields = ['visitor_name', 'visitor_email', 'pass_code', 'purpose']
    filterset_fields = ['status', 'scheduled_date', 'building']
    ordering_fields = ['scheduled_date', 'created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        qs = VisitorPass.objects.select_related(
            'company', 'host', 'building', 'created_by'
        )
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'cancel']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        visitor = self.get_object()
        if visitor.status != VisitorPass.SCHEDULED:
            return Response(
                {'detail': 'Only scheduled passes can be checked in.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        visitor.status = VisitorPass.CHECKED_IN
        visitor.checked_in_at = timezone.now()
        visitor.save(update_fields=['status', 'checked_in_at', 'updated_at'])

        from apps.notifications.tasks import notify_visitor_arrival
        notify_visitor_arrival.delay(str(visitor.pk))

        return Response(self.get_serializer(visitor).data)

    @action(detail=True, methods=['post'], url_path='check-out')
    def check_out(self, request, pk=None):
        visitor = self.get_object()
        if visitor.status != VisitorPass.CHECKED_IN:
            return Response(
                {'detail': 'Only checked-in visitors can be checked out.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        visitor.status = VisitorPass.CHECKED_OUT
        visitor.checked_out_at = timezone.now()
        visitor.save(update_fields=['status', 'checked_out_at', 'updated_at'])
        return Response(self.get_serializer(visitor).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        visitor = self.get_object()
        if visitor.status in [VisitorPass.CHECKED_OUT, VisitorPass.CANCELLED]:
            return Response(
                {'detail': 'Cannot cancel a completed or already-cancelled pass.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        visitor.status = VisitorPass.CANCELLED
        visitor.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(visitor).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_pass(request, pass_code):
    """QR-scan endpoint — no auth. Returns minimal pass info by pass code."""
    try:
        visitor = VisitorPass.objects.select_related('host', 'building').get(
            pass_code=pass_code.upper()
        )
    except VisitorPass.DoesNotExist:
        return Response({'detail': 'Invalid pass code.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(VisitorPassPublicSerializer(visitor).data)
