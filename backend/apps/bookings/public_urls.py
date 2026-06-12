from django.urls import path
from . import public_views

urlpatterns = [
    path('facilities/', public_views.PublicFacilityListView.as_view(), name='public-facility-list'),
    path('facilities/<uuid:pk>/availability/', public_views.PublicAvailabilityView.as_view(),
         name='public-facility-availability'),
    path('bookings/', public_views.PublicBookingCreateView.as_view(), name='public-booking-create'),
    path('stats/', public_views.PublicStatsView.as_view(), name='public-stats'),
    path('reviews/', public_views.PublicReviewListView.as_view(), name='public-reviews'),
]
