from datetime import date, timedelta

from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsSuperAdmin
from apps.billing.models import Invoice
from apps.bookings.models import Booking
from apps.companies.models import Company
from apps.facilities.models import Facility
from apps.maintenance.models import MaintenanceTicket
from apps.workspace.models import Desk, ParkingSlot


def _date_range(request, default_days=30):
    today = timezone.now().date()
    try:
        start = date.fromisoformat(request.query_params.get('start', ''))
    except (ValueError, TypeError):
        start = today - timedelta(days=default_days)
    try:
        end = date.fromisoformat(request.query_params.get('end', ''))
    except (ValueError, TypeError):
        end = today
    return start, end


def _company_q(user):
    return Q() if user.is_super_admin else Q(company=user.company)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        cq = _company_q(user)

        # Revenue
        inv = Invoice.objects.filter(cq).aggregate(
            total=Sum('total_amount'),
            paid=Sum('total_amount', filter=Q(status='paid')),
            overdue=Sum('total_amount', filter=Q(status='overdue')),
        )

        # Bookings
        bk = Booking.objects.filter(cq).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            completed=Count('id', filter=Q(status='completed')),
            rejected=Count('id', filter=Q(status='rejected')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        )

        # Workspace occupancy
        total_desks = Desk.objects.count()
        assigned_desks = (
            Desk.objects.count() if user.is_super_admin
            else Desk.objects.filter(company=user.company).count()
            if user.company_id else 0
        )
        # For super admin count assigned (non-null company)
        if user.is_super_admin:
            assigned_desks = Desk.objects.filter(company__isnull=False).count()

        total_parking = ParkingSlot.objects.count()
        if user.is_super_admin:
            assigned_parking = ParkingSlot.objects.filter(company__isnull=False).count()
        else:
            assigned_parking = ParkingSlot.objects.filter(company=user.company).count() if user.company_id else 0

        # Maintenance
        mq = Q() if user.is_super_admin else Q(company=user.company)
        maint = MaintenanceTicket.objects.filter(mq).aggregate(
            open=Count('id', filter=Q(status='open')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved_this_month=Count('id', filter=Q(
                status='resolved', resolved_at__date__gte=month_start,
            )),
        )

        data = {
            'as_of': today,
            'revenue': {
                'total_invoiced': float(inv['total'] or 0),
                'total_paid': float(inv['paid'] or 0),
                'total_overdue': float(inv['overdue'] or 0),
                'total_outstanding': float((inv['total'] or 0) - (inv['paid'] or 0)),
            },
            'bookings': {k: (v or 0) for k, v in bk.items()},
            'occupancy': {
                'desks': {
                    'total': total_desks,
                    'assigned': assigned_desks,
                    'rate_pct': round(assigned_desks / total_desks * 100, 1) if total_desks else 0,
                },
                'parking': {
                    'total': total_parking,
                    'assigned': assigned_parking,
                    'rate_pct': round(assigned_parking / total_parking * 100, 1) if total_parking else 0,
                },
            },
            'maintenance': {k: (v or 0) for k, v in maint.items()},
        }

        if user.is_super_admin:
            data['platform'] = {
                'total_companies': Company.objects.count(),
                'active_companies': Company.objects.filter(status='active').count(),
                'total_facilities': Facility.objects.count(),
            }

        return Response(data)


class RevenueAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start, end = _date_range(request, default_days=180)
        period = request.query_params.get('period', 'monthly')

        cq = _company_q(user)
        inv_qs = Invoice.objects.filter(cq, created_at__date__gte=start, created_at__date__lte=end)

        trunc = TruncMonth if period == 'monthly' else TruncDate
        fmt = '%Y-%m' if period == 'monthly' else '%Y-%m-%d'

        by_period = (
            inv_qs
            .annotate(p=trunc('created_at'))
            .values('p')
            .annotate(invoiced=Sum('total_amount'), invoice_count=Count('id'))
            .order_by('p')
        )

        totals = inv_qs.aggregate(
            invoiced=Sum('total_amount'),
            paid=Sum('total_amount', filter=Q(status='paid')),
            invoice_count=Count('id'),
        )

        by_company = []
        if user.is_super_admin:
            by_company = list(
                inv_qs
                .values('company__name')
                .annotate(invoiced=Sum('total_amount'), count=Count('id'))
                .order_by('-invoiced')[:10]
            )

        return Response({
            'start': start,
            'end': end,
            'period': period,
            'by_period': [
                {
                    'period': row['p'].strftime(fmt),
                    'invoiced': float(row['invoiced'] or 0),
                    'invoice_count': row['invoice_count'],
                }
                for row in by_period
            ],
            'totals': {
                'invoiced': float(totals['invoiced'] or 0),
                'paid': float(totals['paid'] or 0),
                'invoice_count': totals['invoice_count'] or 0,
            },
            'by_company': [
                {
                    'company': row['company__name'],
                    'invoiced': float(row['invoiced'] or 0),
                    'count': row['count'],
                }
                for row in by_company
            ],
        })


class BookingAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start, end = _date_range(request, default_days=30)
        cq = _company_q(user)

        bk_qs = Booking.objects.filter(cq, booking_date__gte=start, booking_date__lte=end)

        by_status = {
            row['status']: row['count']
            for row in bk_qs.values('status').annotate(count=Count('id'))
        }

        by_facility = list(
            bk_qs
            .values('facility__name')
            .annotate(bookings=Count('id'), revenue=Sum('total_amount'))
            .order_by('-bookings')[:10]
        )

        weekday_counts = [0] * 7
        for row in bk_qs.values('booking_date').annotate(count=Count('id')):
            weekday_counts[row['booking_date'].weekday()] += row['count']

        avg = bk_qs.filter(status='completed').aggregate(avg_dur=Avg('duration_hours'))
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        return Response({
            'start': start,
            'end': end,
            'total': bk_qs.count(),
            'avg_duration_hours': round(float(avg['avg_dur'] or 0), 2),
            'by_status': by_status,
            'by_facility': [
                {
                    'facility': row['facility__name'],
                    'bookings': row['bookings'],
                    'revenue': float(row['revenue'] or 0),
                }
                for row in by_facility
            ],
            'by_weekday': [
                {'day': days[i], 'bookings': weekday_counts[i]} for i in range(7)
            ],
        })


class OccupancyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        desk_stats = Desk.objects.aggregate(
            total=Count('id'),
            assigned=Count('id', filter=Q(company__isnull=False)),
            dedicated=Count('id', filter=Q(desk_type='dedicated')),
            hot_desk=Count('id', filter=Q(desk_type='hot_desk')),
        )
        parking_stats = ParkingSlot.objects.aggregate(
            total=Count('id'),
            assigned=Count('id', filter=Q(company__isnull=False)),
            car=Count('id', filter=Q(slot_type='car')),
            bike=Count('id', filter=Q(slot_type='bike')),
            ev=Count('id', filter=Q(slot_type='ev')),
        )

        dt = desk_stats['total'] or 1
        pt = parking_stats['total'] or 1

        return Response({
            'desks': {
                **desk_stats,
                'occupancy_rate_pct': round(desk_stats['assigned'] / dt * 100, 1),
            },
            'parking': {
                **parking_stats,
                'occupancy_rate_pct': round(parking_stats['assigned'] / pt * 100, 1),
            },
        })


# ─── Report downloads ─────────────────────────────────────

class RevenueReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _date_range(request, default_days=30)
        fmt = request.query_params.get('format', 'pdf')

        # Re-use the analytics view logic
        data = RevenueAnalyticsView().get(request).data

        if fmt == 'excel':
            from .reports import generate_revenue_excel
            buf = generate_revenue_excel(data, start, end)
            resp = HttpResponse(
                buf.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            resp['Content-Disposition'] = f'attachment; filename="revenue_{start}_{end}.xlsx"'
        else:
            from .reports import generate_revenue_pdf
            buf = generate_revenue_pdf(data, start, end)
            resp = HttpResponse(buf.read(), content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="revenue_{start}_{end}.pdf"'

        return resp


class BookingReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _date_range(request, default_days=30)
        fmt = request.query_params.get('format', 'pdf')

        data = BookingAnalyticsView().get(request).data

        if fmt == 'excel':
            from .reports import generate_booking_excel
            buf = generate_booking_excel(data, start, end)
            resp = HttpResponse(
                buf.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            resp['Content-Disposition'] = f'attachment; filename="bookings_{start}_{end}.xlsx"'
        else:
            from .reports import generate_booking_pdf
            buf = generate_booking_pdf(data, start, end)
            resp = HttpResponse(buf.read(), content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="bookings_{start}_{end}.pdf"'

        return resp
