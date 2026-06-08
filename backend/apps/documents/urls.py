from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentVersionViewSet

router = DefaultRouter()
router.register('', DocumentViewSet, basename='document')
router.register('versions', DocumentVersionViewSet, basename='document-version')

urlpatterns = [
    path('', include(router.urls)),
]
