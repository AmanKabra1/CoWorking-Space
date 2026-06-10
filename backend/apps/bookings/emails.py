"""Transactional emails for the booking flow (best-effort, never blocks)."""
from apps.accounts.models import User
from apps.notifications.email import send_email


def _super_admin_emails():
    return list(
        User.objects.filter(role=User.SUPER_ADMIN, is_active=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )


def _slot(booking):
    return f"{booking.booking_date} {booking.start_time}–{booking.end_time}"


def notify_admins_new_public_booking(booking):
    """Tell super admins a public visitor requested a booking."""
    subject = f"New booking request — {booking.facility.name}"
    body = (
        "A public booking request was submitted and needs review.\n\n"
        f"Facility: {booking.facility.name}\n"
        f"When: {_slot(booking)}\n"
        f"Guest: {booking.guest_name} ({booking.guest_email}, {booking.guest_phone})\n"
        f"Company: {booking.guest_company or '—'}\n"
        f"Attendees: {booking.attendees_count}\n"
        f"Purpose: {booking.purpose}\n"
        f"Amount: INR {booking.total_amount}\n\n"
        "Open the CoWorkHub dashboard to approve or reject it."
    )
    for email in _super_admin_emails():
        send_email(email, subject, body)


def notify_guest_booking_approved(booking):
    """Tell the guest their booking was approved (payment details follow in A3)."""
    if not booking.guest_email:
        return
    subject = f"Your booking is approved — {booking.facility.name}"
    body = (
        f"Hi {booking.guest_name},\n\n"
        f"Good news — your booking for {booking.facility.name} on {_slot(booking)} has been approved.\n"
        f"Amount due: INR {booking.total_amount}.\n\n"
        "You'll receive payment instructions shortly. Your slot is held pending payment.\n\n"
        "Thank you for choosing CoWorkHub."
    )
    send_email(booking.guest_email, subject, body)


def notify_guest_booking_rejected(booking):
    """Tell the guest their booking request was declined."""
    if not booking.guest_email:
        return
    subject = f"Update on your booking request — {booking.facility.name}"
    body = (
        f"Hi {booking.guest_name},\n\n"
        f"Unfortunately your booking request for {booking.facility.name} on {_slot(booking)} "
        "could not be approved.\n"
    )
    if booking.rejection_reason:
        body += f"Reason: {booking.rejection_reason}\n"
    body += "\nYou're welcome to submit another request for a different slot."
    send_email(booking.guest_email, subject, body)
