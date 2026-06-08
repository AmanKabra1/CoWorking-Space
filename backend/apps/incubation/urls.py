from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProfileViewSet, IncubationApplicationViewSet, FundingRoundViewSet

router = DefaultRouter()
router.register('profiles', StartupProfileViewSet, basename='startup-profile')
router.register('applications', IncubationApplicationViewSet, basename='incubation-application')
router.register('funding', FundingRoundViewSet, basename='funding-round')

urlpatterns = [
    path('', include(router.urls)),
]
