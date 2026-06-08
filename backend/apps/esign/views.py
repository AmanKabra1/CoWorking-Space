import io
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.esign.models import SignatureRequest, SignatureRecord
from apps.esign.serializers import (
    SignatureRequestSerializer, SignActionSerializer, DeclineActionSerializer
)
from apps.esign.certificate import generate_certificate


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


class SignatureRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SignatureRequestSerializer

    def get_queryset(self):
        user = self.request.user
        qs = SignatureRequest.objects.select_related('created_by', 'company').prefetch_related('records')
        if user.is_super_admin:
            return qs
        return qs.filter(company=user.company)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        req = self.get_object()
        if req.status in (SignatureRequest.COMPLETED, SignatureRequest.CANCELLED):
            return Response({'detail': 'Cannot cancel.'}, status=400)
        req.status = SignatureRequest.CANCELLED
        req.save(update_fields=['status', 'updated_at'])
        return Response({'status': 'cancelled'})


@api_view(['GET'])
@permission_classes([AllowAny])
def signing_detail(request, token):
    """Public: retrieve signing request by token (for signer preview)."""
    try:
        record = SignatureRecord.objects.select_related('request', 'request__created_by').get(
            signing_token=token
        )
    except SignatureRecord.DoesNotExist:
        return Response({'detail': 'Invalid or expired signing link.'}, status=404)

    if record.status != SignatureRecord.PENDING:
        return Response({'detail': f'Already {record.status}.'}, status=400)

    req = record.request
    return Response({
        'title': req.title,
        'message': req.message,
        'document_url': request.build_absolute_uri(req.document_file.url) if req.document_file else None,
        'signer_name': record.signer_name,
        'signer_email': record.signer_email,
        'expires_at': req.expires_at.isoformat() if req.expires_at else None,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_document(request, token):
    """Public: submit signature."""
    try:
        record = SignatureRecord.objects.select_related('request').get(signing_token=token)
    except SignatureRecord.DoesNotExist:
        return Response({'detail': 'Invalid link.'}, status=404)

    if record.status != SignatureRecord.PENDING:
        return Response({'detail': f'Already {record.status}.'}, status=400)

    serializer = SignActionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    record.status = SignatureRecord.SIGNED
    record.signed_at = timezone.now()
    record.signature_data = serializer.validated_data['signature_data']
    record.ip_address = _get_client_ip(request)
    record.save()

    req = record.request
    req._refresh_status()

    if req.status == SignatureRequest.COMPLETED:
        _attach_certificate(req)

    return Response({'detail': 'Signed successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def decline_document(request, token):
    """Public: decline signing."""
    try:
        record = SignatureRecord.objects.select_related('request').get(signing_token=token)
    except SignatureRecord.DoesNotExist:
        return Response({'detail': 'Invalid link.'}, status=404)

    if record.status != SignatureRecord.PENDING:
        return Response({'detail': f'Already {record.status}.'}, status=400)

    serializer = DeclineActionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    record.status = SignatureRecord.DECLINED
    record.decline_reason = serializer.validated_data.get('reason', '')
    record.ip_address = _get_client_ip(request)
    record.save()

    return Response({'detail': 'Declined.'})


def _attach_certificate(req):
    try:
        pdf_bytes = generate_certificate(req)
        req.certificate_file.save(
            f'certificate_{req.id}.pdf',
            ContentFile(pdf_bytes),
            save=True,
        )
    except Exception:
        pass
