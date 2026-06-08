from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisitorPassViewSet, verify_pass

router = DefaultRouter()
router.register('passes', VisitorPassViewSet, basename='visitor-pass')

urlpatterns = [
    path('', include(router.urls)),
    path('verify/<str:pass_code>/', verify_pass, name='verify-visitor-pass'),
]
