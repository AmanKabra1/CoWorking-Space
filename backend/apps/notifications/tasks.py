"""
Celery tasks for notification delivery.
All tasks are retried up to 3 times on failure with a 60-second backoff.
"""
import logging
from celery import shared_task
from django.utils import timezone

from .email import send_email
from .models import Notification

logger = logging.getLogger(__name__)


# ─── Booking notifications ────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_booking_status(self, booking_id, event):
    """
    event: 'approved' | 'rejected' | 'cancelled'
    Called from booking views after status transitions.
    """
    try:
        from apps.bookings.models import Booking
        booking = Booking.objects.select_related(
            'booked_by', 'facility', 'company'
        ).get(pk=booking_id)

        titles = {
            'approved': f"Booking Approved — {booking.facility.name}",
            'rejected': f"Booking Rejected — {booking.facility.name}",
            'cancelled': f"Booking Cancelled — {booking.facility.name}",
        }
        notif_types = {
            'approved': 'booking_approved',
            'rejected': 'booking_rejected',
            'cancelled': 'booking_cancelled',
        }
        messages = {
            'approved': (
                f"Your booking for {booking.facility.name} on "
                f"{booking.booking_date} ({booking.start_time}–{booking.end_time}) has been approved."
            ),
            'rejected': (
                f"Your booking for {booking.facility.name} on "
                f"{booking.booking_date} has been rejected."
            ),
            'cancelled': (
                f"Your booking (#{booking.id}) for {booking.facility.name} has been cancelled."
            ),
        }

        title = titles.get(event, 'Booking Update')
        message = messages.get(event, '')
        notif_type = notif_types.get(event, 'system')

        Notification.create_for_user(
            user=booking.booked_by,
            title=title,
            message=message,
            notification_type=notif_type,
            related_id=booking.id,
            related_type='booking',
        )
        send_email(booking.booked_by.email, title, message)

    except Exception as exc:
        logger.error("notify_booking_status failed for booking %s: %s", booking_id, exc)
        raise self.retry(exc=exc)


# ─── Invoice notifications ────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_invoice_sent(self, invoice_id):
    try:
        from apps.billing.models import Invoice
        invoice = Invoice.objects.select_related('company').get(pk=invoice_id)
        admins = invoice.company.employees.filter(role='company_admin')

        title = f"Invoice {invoice.invoice_number} — ₹{invoice.total_amount}"
        message = (
            f"Invoice {invoice.invoice_number} for ₹{invoice.total_amount} "
            f"has been sent. Due date: {invoice.due_date}."
        )
        for admin in admins:
            Notification.create_for_user(
                user=admin, title=title, message=message,
                notification_type='invoice_sent',
                related_id=invoice.id, related_type='invoice',
            )
            send_email(admin.email, title, message)

    except Exception as exc:
        logger.error("notify_invoice_sent failed for invoice %s: %s", invoice_id, exc)
        raise self.retry(exc=exc)


# ─── Maintenance notifications ────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_ticket_assigned(self, ticket_id):
    try:
        from apps.maintenance.models import MaintenanceTicket
        ticket = MaintenanceTicket.objects.select_related(
            'assigned_to', 'reported_by', 'company'
        ).get(pk=ticket_id)

        if not ticket.assigned_to:
            return

        title = f"Ticket Assigned — {ticket.ticket_number}"
        message = (
            f"You have been assigned maintenance ticket {ticket.ticket_number}: "
            f"'{ticket.title}' (Priority: {ticket.get_priority_display()})."
        )
        Notification.create_for_user(
            user=ticket.assigned_to, title=title, message=message,
            notification_type='maintenance_assigned',
            related_id=ticket.id, related_type='maintenance_ticket',
        )
        send_email(ticket.assigned_to.email, title, message)

    except Exception as exc:
        logger.error("notify_ticket_assigned failed for ticket %s: %s", ticket_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_ticket_resolved(self, ticket_id):
    try:
        from apps.maintenance.models import MaintenanceTicket
        ticket = MaintenanceTicket.objects.select_related(
            'reported_by', 'assigned_to'
        ).get(pk=ticket_id)

        if not ticket.reported_by:
            return

        title = f"Ticket Resolved — {ticket.ticket_number}"
        message = (
            f"Your maintenance ticket {ticket.ticket_number} ('{ticket.title}') "
            f"has been resolved. Notes: {ticket.resolution_notes or 'N/A'}"
        )
        Notification.create_for_user(
            user=ticket.reported_by, title=title, message=message,
            notification_type='maintenance_resolved',
            related_id=ticket.id, related_type='maintenance_ticket',
        )
        send_email(ticket.reported_by.email, title, message)

    except Exception as exc:
        logger.error("notify_ticket_resolved failed for ticket %s: %s", ticket_id, exc)
        raise self.retry(exc=exc)


# ─── Visitor notifications ────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_visitor_arrival(self, pass_id):
    try:
        from apps.visitors.models import VisitorPass
        visitor = VisitorPass.objects.select_related('host').get(pk=pass_id)

        title = f"Visitor Arrived — {visitor.visitor_name}"
        message = (
            f"{visitor.visitor_name} has checked in at {timezone.now().strftime('%H:%M')}. "
            f"Purpose: {visitor.purpose}"
        )
        Notification.create_for_user(
            user=visitor.host, title=title, message=message,
            notification_type='visitor_arrival',
            related_id=visitor.id, related_type='visitor_pass',
        )
        send_email(visitor.host.email, title, message)

    except Exception as exc:
        logger.error("notify_visitor_arrival failed for pass %s: %s", pass_id, exc)
        raise self.retry(exc=exc)


# ─── Periodic tasks (Celery Beat) ────────────────────────

@shared_task
def check_overdue_invoices():
    """
    Runs daily at 9 AM IST (configured in CELERY_BEAT_SCHEDULE).
    Marks sent invoices past their due date as overdue and notifies company admins.
    """
    from apps.billing.models import Invoice
    today = timezone.now().date()

    overdue_invoices = Invoice.objects.filter(
        status='sent', due_date__lt=today
    ).select_related('company')

    count = 0
    for invoice in overdue_invoices:
        invoice.status = 'overdue'
        invoice.save(update_fields=['status', 'updated_at'])

        title = f"Invoice Overdue — {invoice.invoice_number}"
        message = (
            f"Invoice {invoice.invoice_number} for ₹{invoice.total_amount} "
            f"was due on {invoice.due_date} and is now overdue."
        )
        admins = invoice.company.employees.filter(role='company_admin')
        for admin in admins:
            Notification.create_for_user(
                user=admin, title=title, message=message,
                notification_type='invoice_overdue',
                related_id=invoice.id, related_type='invoice',
            )
            send_email(admin.email, title, message)
        count += 1

    logger.info("check_overdue_invoices: marked %d invoices as overdue", count)
    return count
