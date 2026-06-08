from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Company
from .serializers import CompanySerializer, CompanyListSerializer
from .permissions import CanViewOwnCompany
from apps.accounts.models import User
from apps.accounts.serializers import UserListSerializer, UserRegistrationSerializer
from apps.accounts.permissions import IsSuperAdmin, IsSuperAdminOrCompanyAdmin


@extend_schema_view(
    list=extend_schema(tags=['Companies']),
    retrieve=extend_schema(tags=['Companies']),
    create=extend_schema(tags=['Companies']),
    update=extend_schema(tags=['Companies']),
    partial_update=extend_schema(tags=['Companies']),
    destroy=extend_schema(tags=['Companies']),
)
class CompanyViewSet(viewsets.ModelViewSet):
    """
    CRUD for Companies (tenants).

    - Super Admin: full access to all companies
    - Company Admin / Employee: read-only access to their own company
    """
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Company.objects.all()
        if user.company_id:
            return Company.objects.filter(id=user.company_id)
        return Company.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        if self.action in ['update', 'partial_update']:
            return [IsSuperAdminOrCompanyAdmin()]
        # list, retrieve — authenticated users limited by queryset
        return [permissions.IsAuthenticated(), CanViewOwnCompany()]

    # ─── Custom actions ───────────────────────────────────

    @extend_schema(tags=['Companies'], responses=UserListSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='employees')
    def employees(self, request, pk=None):
        """List active employees of this company."""
        company = self.get_object()
        employees = (
            company.employees
            .filter(is_active=True)
            .select_related('company')
            .order_by('first_name', 'last_name')
        )
        serializer = UserListSerializer(employees, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Companies'],
        request=UserRegistrationSerializer,
        responses={201: UserListSerializer},
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='invite-employee',
        permission_classes=[IsSuperAdmin],
    )
    def invite_employee(self, request, pk=None):
        """
        Create a new Employee or Company Admin user and assign them to this company.
        Super Admin only.
        """
        company = self.get_object()
        data = request.data.copy()
        # Default role to employee if not provided; block super_admin creation here
        if data.get('role') == User.SUPER_ADMIN:
            return Response(
                {'detail': 'Cannot create Super Admin via company invite.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserRegistrationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(company=company)
        return Response(UserListSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Companies'])
    @action(
        detail=True,
        methods=['patch'],
        url_path='status',
        permission_classes=[IsSuperAdmin],
    )
    def set_status(self, request, pk=None):
        """Activate, deactivate, or suspend a company. Super Admin only."""
        company = self.get_object()
        new_status = request.data.get('status')
        valid = [c[0] for c in Company.STATUS_CHOICES]
        if new_status not in valid:
            return Response(
                {'detail': f'status must be one of: {valid}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        company.status = new_status
        company.save(update_fields=['status', 'updated_at'])
        return Response(CompanySerializer(company).data)
