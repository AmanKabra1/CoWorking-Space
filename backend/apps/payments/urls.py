from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaymentGatewayViewSet, PaymentOrderViewSet, razorpay_webhook, stripe_webhook

router = DefaultRouter()
router.register('gateways', PaymentGatewayViewSet, basename='payment-gateway')
router.register('payment-orders', PaymentOrderViewSet, basename='payment-order')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/razorpay/', razorpay_webhook, name='razorpay-webhook'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
