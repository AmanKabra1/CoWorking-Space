from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check (no auth required — used by load balancers / Render)
    path('api/', include('apps.core.urls')),

    # API v1
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/companies/', include('apps.companies.urls')),
    path('api/v1/workspace/', include('apps.workspace.urls')),
    path('api/v1/facilities/', include('apps.facilities.urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/billing/', include('apps.billing.urls')),
    path('api/v1/ai/', include('apps.ai_assistant.urls')),
    path('api/v1/incubation/', include('apps.incubation.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/maintenance/', include('apps.maintenance.urls')),
    path('api/v1/visitors/', include('apps.visitors.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
    path('api/v1/community/', include('apps.community.urls')),
    path('api/v1/esign/', include('apps.esign.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/vendors/', include('apps.vendors.urls')),
    path('api/v1/subleasing/', include('apps.subleasing.urls')),
    path('api/v1/public/', include('apps.bookings.public_urls')),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
