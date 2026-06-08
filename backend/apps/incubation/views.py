from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsSuperAdmin, IsSuperAdminOrCompanyAdmin
from .models import StartupProfile, IncubationApplication, ApplicationNote, FundingRound
from .serializers import (
    StartupProfileSerializer,
    IncubationApplicationSerializer,
    ApplicationNoteSerializer,
    RejectApplicationSerializer,
    FundingRoundSerializer,
)


class StartupProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StartupProfileSerializer
    search_fields = ['startup_name', 'company__name']
    filterset_fields = ['industry', 'stage']
    ordering_fields = ['startup_name', 'founded_date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = StartupProfile.objects.select_related('company').prefetch_related('applications')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]


class IncubationApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = IncubationApplicationSerializer
    filterset_fields = ['status', 'cohort', 'funding_type']
    search_fields = ['startup__startup_name', 'startup__company__name', 'cohort']
    ordering_fields = ['submitted_at', 'created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        qs = IncubationApplication.objects.select_related(
            'startup__company', 'reviewed_by'
        ).prefetch_related('notes__author')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(startup__company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['review', 'accept', 'reject']:
            return [IsSuperAdmin()]
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'submit', 'withdraw', 'add_note']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        application = self.get_object()
        if application.status != IncubationApplication.DRAFT:
            return Response(
                {'detail': 'Only draft applications can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = IncubationApplication.SUBMITTED
        application.submitted_at = timezone.now()
        application.save(update_fields=['status', 'submitted_at', 'updated_at'])
        return Response(self.get_serializer(application).data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        application = self.get_object()
        if application.status != IncubationApplication.SUBMITTED:
            return Response(
                {'detail': 'Only submitted applications can be moved to review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = IncubationApplication.UNDER_REVIEW
        application.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(application).data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        application = self.get_object()
        if application.status not in [
            IncubationApplication.SUBMITTED, IncubationApplication.UNDER_REVIEW
        ]:
            return Response(
                {'detail': 'Only submitted or under-review applications can be accepted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = IncubationApplication.ACCEPTED
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])
        return Response(self.get_serializer(application).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        application = self.get_object()
        if application.status not in [
            IncubationApplication.SUBMITTED, IncubationApplication.UNDER_REVIEW
        ]:
            return Response(
                {'detail': 'Only submitted or under-review applications can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = RejectApplicationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        application.status = IncubationApplication.REJECTED
        application.rejection_reason = ser.validated_data['reason']
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=[
            'status', 'rejection_reason', 'reviewed_by', 'reviewed_at', 'updated_at'
        ])
        return Response(self.get_serializer(application).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        if application.status in [
            IncubationApplication.ACCEPTED, IncubationApplication.REJECTED
        ]:
            return Response(
                {'detail': 'Accepted or rejected applications cannot be withdrawn.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = IncubationApplication.WITHDRAWN
        application.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(application).data)

    @action(detail=True, methods=['get'], url_path='notes')
    def get_notes(self, request, pk=None):
        application = self.get_object()
        qs = application.notes.select_related('author')
        if not request.user.is_super_admin:
            qs = qs.filter(is_internal=False)
        return Response(
            ApplicationNoteSerializer(qs, many=True, context={'request': request}).data
        )

    @action(detail=True, methods=['post'], url_path='notes/add',
            permission_classes=[IsSuperAdminOrCompanyAdmin])
    def add_note(self, request, pk=None):
        application = self.get_object()
        serializer = ApplicationNoteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(application=application, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FundingRoundViewSet(viewsets.ModelViewSet):
    serializer_class = FundingRoundSerializer
    filterset_fields = ['status', 'funding_type', 'currency']
    ordering_fields = ['amount_sought', 'target_date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = FundingRound.objects.select_related('startup__company')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(startup__company=user.company)
        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [IsAuthenticated()]
