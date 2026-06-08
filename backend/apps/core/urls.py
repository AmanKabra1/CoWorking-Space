from django.http import JsonResponse
from django.urls import path
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    Lightweight liveness + readiness probe.
    Returns 200 if DB and cache are reachable, 503 otherwise.
    Used by Docker healthcheck, load balancers, and Render's healthCheckPath.
    """
    checks = {}

    # Database
    try:
        connection.ensure_connection()
        checks['db'] = 'ok'
    except Exception as e:
        checks['db'] = f'error: {e}'

    # Cache (Redis)
    try:
        cache.set('health_probe', '1', timeout=5)
        checks['cache'] = 'ok' if cache.get('health_probe') == '1' else 'miss'
    except Exception as e:
        checks['cache'] = f'error: {e}'

    healthy = all(v == 'ok' for v in checks.values())
    return JsonResponse(
        {'status': 'ok' if healthy else 'degraded', 'checks': checks},
        status=200 if healthy else 503,
    )


urlpatterns = [
    path('health/', health_check, name='health-check'),
]
