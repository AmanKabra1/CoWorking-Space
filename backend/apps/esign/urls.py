from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.esign.views import SignatureRequestViewSet, signing_detail, sign_document, decline_document

router = DefaultRouter()
router.register('requests', SignatureRequestViewSet, basename='signature-request')

urlpatterns = router.urls + [
    path('sign/<uuid:token>/', signing_detail, name='esign-detail'),
    path('sign/<uuid:token>/submit/', sign_document, name='esign-submit'),
    path('sign/<uuid:token>/decline/', decline_document, name='esign-decline'),
]
