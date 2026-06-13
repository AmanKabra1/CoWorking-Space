from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
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

    @extend_schema(tags=['Companies'], responses=CompanySerializer)
    @action(
        detail=True,
        methods=['post'],
        url_path='regenerate-join-code',
        permission_classes=[IsSuperAdminOrCompanyAdmin],
    )
    def regenerate_join_code(self, request, pk=None):
        """
        Issue a fresh join code (invalidates the old one). Super Admin for any
        company; Company Admin only for their own (enforced by the queryset).
        """
        company = self.get_object()
        company.join_code = Company.new_unique_join_code()
        company.save(update_fields=['join_code', 'updated_at'])
        return Response(CompanySerializer(company).data)

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


@extend_schema(tags=['Companies'])
class CompanySettingsView(APIView):
    """
    GET /api/v1/companies/settings/  — retrieve current company profile.
    PATCH /api/v1/companies/settings/ — update current company profile.

    Resolves the company via TenantMiddleware (request.company) when available,
    falling back to the authenticated user's company.
    Accessible to company_admin and super_admin only.
    """

    permission_classes = [IsSuperAdminOrCompanyAdmin]

    def _get_company(self, request):
        company = getattr(request, 'company', None)
        if company is None:
            company = getattr(request.user, 'company', None)
        return company

    def get(self, request):
        company = self._get_company(request)
        if company is None:
            return Response(
                {'detail': 'No company associated with this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def patch(self, request):
        company = self._get_company(request)
        if company is None:
            return Response(
                {'detail': 'No company associated with this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
