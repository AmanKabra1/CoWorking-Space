from django.urls import path
from .views import (
    DashboardView,
    RevenueAnalyticsView,
    BookingAnalyticsView,
    OccupancyView,
    RevenueReportView,
    BookingReportView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='analytics-dashboard'),
    path('revenue/', RevenueAnalyticsView.as_view(), name='analytics-revenue'),
    path('bookings/', BookingAnalyticsView.as_view(), name='analytics-bookings'),
    path('occupancy/', OccupancyView.as_view(), name='analytics-occupancy'),
    path('reports/revenue/', RevenueReportView.as_view(), name='report-revenue'),
    path('reports/bookings/', BookingReportView.as_view(), name='report-bookings'),
]
