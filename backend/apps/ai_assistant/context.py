"""
Context builders — fetch relevant DB data and format it for the AI prompt.
Keeps the AI grounded in real data (RAG-lite pattern without vector embeddings).
"""
from django.utils import timezone


def build_system_prompt(user) -> str:
    """
    Build the system/persona prompt with live company data injected.
    Called once per conversation to set context.
    """
    role_desc = {
        'super_admin': 'platform super administrator with access to all companies and data',
        'company_admin': 'company administrator managing their organisation',
        'employee': 'employee of the company',
    }.get(user.role, 'user')

    company_block = ''
    if user.company:
        co = user.company
        company_block = f"""
Current company context:
  Name: {co.name}
  Status: {co.get_status_display()}
  City: {co.city}, {co.state}
  GST: {co.gst_number or 'Not set'}
  Contract: {co.contract_start} to {co.contract_end or 'ongoing'}
"""

    return f"""You are CoWorkHub Assistant — an intelligent AI helper embedded in a professional \
coworking space management platform called CoWorkHub built by Sanchi Connect.

The user is: {user.get_full_name()} ({user.email})
Role: {role_desc}
{company_block}
Platform capabilities:
- Workspace management (buildings, floors, rooms, desks, parking)
- Facility booking (conference rooms, meeting rooms, event halls, podcast studios, etc.)
- Booking workflow: pending → approved → completed/cancelled
- GST-compliant billing with UPI QR code PDF invoices
- Role-based access: Super Admin / Company Admin / Employee

Guidelines:
- Answer only questions relevant to coworking space management, bookings, billing, or platform usage
- For data questions, use the context provided; do not hallucinate specific IDs or amounts
- Be concise and professional. Use bullet points for lists
- If asked something outside your scope, politely redirect
- Always respond in the same language the user writes in
- Today is {timezone.localdate()}
"""


def build_company_context(user) -> str:
    """
    Fetch live data for the user's company and format as readable context.
    Injected into every user message so the AI can answer data questions.
    """
    from apps.bookings.models import Booking
    from apps.billing.models import Invoice
    from apps.facilities.models import Facility
    from apps.workspace.models import Desk, ParkingSlot

    lines = []
    today = timezone.localdate()

    if user.is_super_admin:
        # Platform-wide snapshot for super admin
        total_bookings = Booking.objects.count()
        pending = Booking.objects.filter(status=Booking.PENDING).count()
        overdue_inv = Invoice.objects.filter(status=Invoice.OVERDUE).count()
        lines.append(f"[Platform snapshot — {today}]")
        lines.append(f"Total bookings: {total_bookings} | Pending approval: {pending}")
        lines.append(f"Overdue invoices: {overdue_inv}")

        upcoming = Booking.objects.filter(
            booking_date__gte=today, status=Booking.APPROVED
        ).select_related('facility', 'company').order_by('booking_date', 'start_time')[:5]
        if upcoming:
            lines.append("Upcoming approved bookings (next 5):")
            for b in upcoming:
                lines.append(f"  • {b.booking_date} {b.start_time}–{b.end_time} | {b.facility.name} | {b.company.name} | Rs {b.total_amount}")

    elif user.company:
        co = user.company
        lines.append(f"[{co.name} data snapshot — {today}]")

        # Desk & parking
        desks = Desk.objects.filter(company=co, desk_type=Desk.DEDICATED).count()
        parking = ParkingSlot.objects.filter(company=co).count()
        lines.append(f"Dedicated desks assigned: {desks} | Parking slots: {parking}")

        # My upcoming bookings
        upcoming = Booking.objects.filter(
            company=co, booking_date__gte=today,
            status__in=[Booking.PENDING, Booking.APPROVED],
        ).select_related('facility').order_by('booking_date', 'start_time')[:5]
        if upcoming:
            lines.append("Upcoming bookings:")
            for b in upcoming:
                lines.append(f"  • {b.booking_date} {b.start_time}–{b.end_time} | {b.facility.name} | {b.get_status_display()} | Rs {b.total_amount}")
        else:
            lines.append("No upcoming bookings.")

        # Latest invoice
        latest_inv = Invoice.objects.filter(company=co).order_by('-created_at').first()
        if latest_inv:
            lines.append(f"Latest invoice: {latest_inv.invoice_number} — Rs {latest_inv.total_amount} ({latest_inv.get_status_display()}) due {latest_inv.due_date}")

        # Pending invoices count
        pending_inv = Invoice.objects.filter(company=co, status__in=[Invoice.SENT, Invoice.OVERDUE]).count()
        if pending_inv:
            lines.append(f"Unpaid invoices: {pending_inv}")

    # Available facilities (everyone can see)
    facilities = Facility.objects.filter(is_active=True).select_related('building')[:8]
    if facilities:
        lines.append("Active facilities:")
        for f in facilities:
            lines.append(f"  • {f.name} ({f.get_facility_type_display()}) — cap {f.capacity} — Rs {f.price_per_hour}/hr | Rs {f.price_per_day}/day")

    return "\n".join(lines) if lines else "No company data available."


def build_booking_suggestions_context(facility, date) -> str:
    """Context for the booking suggestion endpoint."""
    from apps.bookings.models import Booking

    booked_slots = Booking.objects.filter(
        facility=facility,
        booking_date=date,
        status__in=[Booking.PENDING, Booking.APPROVED],
    ).values_list('start_time', 'end_time', 'status')

    booked_text = "\n".join(
        f"  • {s} – {e} ({st})" for s, e, st in booked_slots
    ) or "  No bookings yet — all slots available."

    return f"""Facility: {facility.name} ({facility.get_facility_type_display()})
Capacity: {facility.capacity} people
Price: Rs {facility.price_per_hour}/hr | Rs {facility.price_per_day}/day
Amenities: {', '.join(facility.amenities) if facility.amenities else 'standard'}
Date: {date}
Already booked slots on this date:
{booked_text}
Business hours assumed: 08:00 – 20:00"""
