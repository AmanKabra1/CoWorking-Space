import logging
from .models import AuditLog

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(user, action, resource_type='', resource_id=None,
               description='', request=None, extra=None):
    """
    Create an AuditLog entry. Call from views after significant actions.

    Example:
        log_action(request.user, 'booking_approved',
                   resource_type='booking', resource_id=booking.id,
                   description=f"Booking {booking.id} approved",
                   request=request)
    """
    try:
        company = getattr(user, 'company', None) if user else None
        ip = _get_client_ip(request) if request else None
        AuditLog.objects.create(
            user=user,
            company=company,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip,
            extra=extra,
        )
    except Exception as exc:
        logger.error("Failed to write audit log [%s]: %s", action, exc)
