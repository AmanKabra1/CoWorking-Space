class TenantMiddleware:
    """
    Resolves the current tenant (Company) from the request and sets request.company.

    Resolution order:
      1. Subdomain — tenant.coworkhub.com  →  slug = "tenant"
      2. X-Company-ID request header (for API / mobile clients)
      3. Authenticated user's company (JWT fallback)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = self._resolve_tenant(request)
        return self.get_response(request)

    def _resolve_tenant(self, request):
        # 1. Subdomain resolution
        host = request.get_host().split(':')[0]
        parts = host.split('.')
        if len(parts) > 2 and parts[0] not in ('www', 'api'):
            from apps.companies.models import Company
            try:
                return Company.objects.get(slug=parts[0], status=Company.ACTIVE)
            except Company.DoesNotExist:
                pass

        # 2. Explicit header (API clients, mobile apps)
        company_id = request.headers.get('X-Company-ID')
        if company_id:
            from apps.companies.models import Company
            try:
                return Company.objects.get(id=company_id, status=Company.ACTIVE)
            except (Company.DoesNotExist, ValueError):
                pass

        # 3. Authenticated user's company (requires AuthenticationMiddleware to run first)
        if hasattr(request, 'user') and request.user.is_authenticated:
            return getattr(request.user, 'company', None)

        return None
