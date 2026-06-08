from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.FacilityViewSet, basename='facility')

urlpatterns = [
    path('', include(router.urls)),
]
