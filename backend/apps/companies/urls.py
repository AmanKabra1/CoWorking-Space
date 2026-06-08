from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.CompanyViewSet, basename='company')

urlpatterns = [
    path('settings/', views.CompanySettingsView.as_view(), name='company-settings'),
    path('', include(router.urls)),
]
