import json
import logging

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from apps.billing.models import Invoice
from .models import PaymentGateway, PaymentOrder
from .serializers import (
    PaymentGatewaySerializer,
    PaymentOrderSerializer,
    CreateOrderSerializer,
    VerifyPaymentSerializer,
)
from .services import RazorpayService, StripeService

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(tags=['Payments']),
    retrieve=extend_schema(tags=['Payments']),
    create=extend_schema(tags=['Payments']),
    update=extend_schema(tags=['Payments']),
    partial_update=extend_schema(tags=['Payments']),
    destroy=extend_schema(tags=['Payments']),
)
class PaymentGatewayViewSet(viewsets.ModelViewSet):
    """Payment gateway configuration per company. Super Admin / Company Admin only."""

    serializer_class = PaymentGatewaySerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return PaymentGateway.objects.select_related('company').all()
        if user.company_id:
            return PaymentGateway.objects.filter(company_id=user.company_id)
        return PaymentGateway.objects.none()


@extend_schema_view(
    list=extend_schema(tags=['Payments']),
    retrieve=extend_schema(tags=['Payments']),
)
class PaymentOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Payment orders — list/retrieve for all authenticated users scoped to their company.
    Admins can create orders and verify payments via custom actions.
    """

    serializer_class = PaymentOrderSerializer

    def get_queryset(self):
        user = self.request.user
        qs = PaymentOrder.objects.select_related('invoice', 'gateway')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(invoice__company_id=user.company_id)
        return PaymentOrder.objects.none()

    def get_permissions(self):
        if self.action in ['create_order', 'verify']:
            return [IsSuperAdminOrCompanyAdmin()]
        return [permissions.IsAuthenticated()]

    @extend_schema(tags=['Payments'], request=CreateOrderSerializer)
    @action(detail=False, methods=['post'], url_path='create_order')
    def create_order(self, request):
        """
        Create a Razorpay order or Stripe PaymentIntent for an invoice.
        Returns gateway data needed by the frontend to launch checkout.
        """
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_id = serializer.validated_data['invoice_id']

        try:
            invoice = Invoice.objects.get(pk=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.status == Invoice.PAID:
            return Response({'detail': 'Invoice is already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gateway = PaymentGateway.objects.get(company=invoice.company, is_active=True)
        except PaymentGateway.DoesNotExist:
            return Response(
                {'detail': 'No active payment gateway configured for this company.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = invoice.total_amount

        if gateway.provider == PaymentGateway.RAZORPAY:
            amount_paise = int(amount * 100)
            receipt = f"inv-{invoice.pk}"
            svc = RazorpayService(gateway.api_key, gateway.api_secret)
            order_data = svc.create_order(amount_paise, 'INR', receipt)
            gateway_order_id = order_data['id']

            payment_order = PaymentOrder.objects.create(
                invoice=invoice,
                gateway=gateway,
                provider=PaymentGateway.RAZORPAY,
                gateway_order_id=gateway_order_id,
                amount=amount,
                currency='INR',
                metadata=order_data,
            )

            return Response({
                'order_id': payment_order.id,
                'gateway_order_id': gateway_order_id,
                'amount': amount_paise,
                'currency': 'INR',
                'key': gateway.api_key,
                'provider': PaymentGateway.RAZORPAY,
            })

        if gateway.provider == PaymentGateway.STRIPE:
            amount_cents = int(amount * 100)
            svc = StripeService(gateway.api_secret)
            intent = svc.create_payment_intent(
                amount_cents,
                'inr',
                {'invoice_id': str(invoice.pk)},
            )

            payment_order = PaymentOrder.objects.create(
                invoice=invoice,
                gateway=gateway,
                provider=PaymentGateway.STRIPE,
                gateway_order_id=intent['id'],
                amount=amount,
                currency='INR',
                metadata={'client_secret': intent['client_secret']},
            )

            return Response({
                'order_id': payment_order.id,
                'gateway_order_id': intent['id'],
                'amount': amount_cents,
                'currency': 'inr',
                'key': gateway.api_key,
                'provider': PaymentGateway.STRIPE,
                'client_secret': intent['client_secret'],
            })

        return Response({'detail': 'Unsupported payment provider.'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['Payments'], request=VerifyPaymentSerializer)
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """Verify payment signature and mark invoice as paid."""
        try:
            payment_order = PaymentOrder.objects.select_related('invoice', 'gateway').get(pk=pk)
        except PaymentOrder.DoesNotExist:
            return Response({'detail': 'Payment order not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if payment_order.provider == PaymentGateway.RAZORPAY:
            payment_id = data.get('payment_id', '')
            signature = data.get('signature', '')
            if not payment_id or not signature:
                return Response(
                    {'detail': 'payment_id and signature are required for Razorpay.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                gateway = payment_order.gateway
                svc = RazorpayService(gateway.api_key, gateway.api_secret)
                svc.verify_payment(payment_order.gateway_order_id, payment_id, signature)
            except Exception:
                payment_order.status = PaymentOrder.FAILED
                payment_order.save(update_fields=['status', 'updated_at'])
                return Response({'detail': 'Payment signature verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

            payment_order.gateway_payment_id = payment_id
            payment_order.status = PaymentOrder.PAID
            payment_order.save(update_fields=['gateway_payment_id', 'status', 'updated_at'])

        elif payment_order.provider == PaymentGateway.STRIPE:
            payment_intent_id = data.get('payment_intent_id', '')
            if not payment_intent_id:
                return Response(
                    {'detail': 'payment_intent_id is required for Stripe.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payment_order.gateway_payment_id = payment_intent_id
            payment_order.status = PaymentOrder.PAID
            payment_order.save(update_fields=['gateway_payment_id', 'status', 'updated_at'])

        else:
            return Response({'detail': 'Unsupported provider.'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = payment_order.invoice
        invoice.status = Invoice.PAID
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['status', 'paid_at', 'updated_at'])

        return Response({'detail': 'Payment verified and invoice marked as paid.'})


@csrf_exempt
def razorpay_webhook(request):
    """Razorpay webhook — verifies signature and marks order PAID or FAILED."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    payload = request.body
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')

    try:
        body = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return HttpResponse(status=400)

    event = body.get('event', '')
    payment_entity = body.get('payload', {}).get('payment', {}).get('entity', {})
    order_id = payment_entity.get('order_id', '')

    if not order_id:
        return HttpResponse(status=200)

    try:
        payment_order = PaymentOrder.objects.select_related('invoice', 'gateway').get(
            gateway_order_id=order_id
        )
    except PaymentOrder.DoesNotExist:
        return HttpResponse(status=200)

    if payment_order.gateway:
        try:
            svc = RazorpayService(payment_order.gateway.api_key, payment_order.gateway.api_secret)
            svc.client.utility.verify_webhook_signature(
                payload.decode('utf-8'),
                webhook_signature,
                payment_order.gateway.api_secret,
            )
        except Exception:
            logger.warning("Razorpay webhook signature verification failed for order %s", order_id)
            return HttpResponse(status=400)

    if event == 'payment.captured':
        payment_order.status = PaymentOrder.PAID
        payment_order.gateway_payment_id = payment_entity.get('id', '')
        payment_order.save(update_fields=['status', 'gateway_payment_id', 'updated_at'])
        invoice = payment_order.invoice
        invoice.status = Invoice.PAID
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['status', 'paid_at', 'updated_at'])

    elif event == 'payment.failed':
        payment_order.status = PaymentOrder.FAILED
        payment_order.save(update_fields=['status', 'updated_at'])

    return HttpResponse(status=200)


@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook — verifies signature and marks order PAID or FAILED."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    import stripe
    from django.conf import settings

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature', '')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        svc = StripeService('')
        event = svc.verify_webhook(payload, sig_header, endpoint_secret)
    except Exception:
        logger.warning("Stripe webhook signature verification failed.")
        return HttpResponse(status=400)

    event_type = event.get('type', '')
    data_object = event.get('data', {}).get('object', {})

    if event_type in ('payment_intent.succeeded', 'payment_intent.payment_failed'):
        intent_id = data_object.get('id', '')
        try:
            payment_order = PaymentOrder.objects.select_related('invoice').get(
                gateway_order_id=intent_id
            )
        except PaymentOrder.DoesNotExist:
            return HttpResponse(status=200)

        if event_type == 'payment_intent.succeeded':
            payment_order.status = PaymentOrder.PAID
            payment_order.gateway_payment_id = intent_id
            payment_order.save(update_fields=['status', 'gateway_payment_id', 'updated_at'])
            invoice = payment_order.invoice
            invoice.status = Invoice.PAID
            invoice.paid_at = timezone.now()
            invoice.save(update_fields=['status', 'paid_at', 'updated_at'])

        elif event_type == 'payment_intent.payment_failed':
            payment_order.status = PaymentOrder.FAILED
            payment_order.save(update_fields=['status', 'updated_at'])

    return HttpResponse(status=200)
