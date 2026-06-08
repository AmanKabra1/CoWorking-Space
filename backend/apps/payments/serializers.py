from rest_framework import serializers

from .models import PaymentGateway, PaymentOrder


class PaymentGatewaySerializer(serializers.ModelSerializer):
    api_secret = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'company', 'provider', 'api_key', 'api_secret',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = [
            'id', 'invoice', 'gateway', 'provider', 'gateway_order_id',
            'gateway_payment_id', 'amount', 'currency', 'status',
            'metadata', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'gateway', 'provider', 'gateway_order_id', 'gateway_payment_id',
            'amount', 'currency', 'status', 'metadata', 'created_at', 'updated_at',
        ]


class CreateOrderSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()


class VerifyPaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField(required=False, allow_blank=True)
    signature = serializers.CharField(required=False, allow_blank=True)
    payment_intent_id = serializers.CharField(required=False, allow_blank=True)
