from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from .models import Document, DocumentVersion
from .serializers import DocumentSerializer, DocumentVersionSerializer, UploadVersionSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['doc_type', 'is_archived']
    ordering_fields = ['title', 'doc_type', 'created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        qs = Document.objects.select_related('company', 'uploaded_by').prefetch_related('versions')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'upload_version', 'archive', 'restore']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]

    @action(
        detail=True, methods=['post'],
        url_path='upload-version',
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_version(self, request, pk=None):
        document = self.get_object()
        serializer = UploadVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data['file']
        last = document.versions.order_by('-version_number').first()
        next_number = (last.version_number + 1) if last else 1

        version = DocumentVersion.objects.create(
            document=document,
            version_number=next_number,
            file=file_obj,
            file_name=file_obj.name,
            file_size=file_obj.size,
            mime_type=getattr(file_obj, 'content_type', ''),
            uploaded_by=request.user,
            change_notes=serializer.validated_data['change_notes'],
        )
        return Response(
            DocumentVersionSerializer(version, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        document = self.get_object()
        qs = document.versions.select_related('uploaded_by').order_by('-version_number')
        return Response(
            DocumentVersionSerializer(qs, many=True, context={'request': request}).data
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        document = self.get_object()
        latest = document.versions.order_by('-version_number').first()
        if not latest or not latest.file:
            return Response({'detail': 'No file available.'}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            latest.file.open('rb'),
            as_attachment=True,
            filename=latest.file_name,
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        document = self.get_object()
        document.is_archived = True
        document.save(update_fields=['is_archived', 'updated_at'])
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        document = self.get_object()
        document.is_archived = False
        document.save(update_fields=['is_archived', 'updated_at'])
        return Response(self.get_serializer(document).data)


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['mime_type']
    ordering_fields = ['version_number', 'created_at', 'file_size']

    def get_queryset(self):
        user = self.request.user
        qs = DocumentVersion.objects.select_related(
            'document__company', 'uploaded_by'
        )
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(document__company=user.company)
        return qs.none()

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        version = self.get_object()
        if not version.file:
            return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            version.file.open('rb'),
            as_attachment=True,
            filename=version.file_name,
        )
