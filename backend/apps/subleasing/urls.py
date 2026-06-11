from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import listing_views

router = DefaultRouter()
# Register specific prefixes before the empty one so they take precedence.
router.register('listings', listing_views.SeatListingViewSet, basename='seat-listing')
router.register('applications', listing_views.SeatApplicationViewSet, basename='seat-application')
router.register('', views.SeatLeaseViewSet, basename='seat-lease')

urlpatterns = [
    path('', include(router.urls)),
]
