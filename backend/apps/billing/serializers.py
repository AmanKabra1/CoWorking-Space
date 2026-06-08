from rest_framework import serializers
from .models import Invoice, Payment


class LineItemSerializer(serializers.Serializer):
    description = serializers.CharField()
    qty = serializers.IntegerField(min_value=1)
    rate = serializers.DecimalField(max_digits=12, decimal_places=2)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'company', 'company_name',
            'amount', 'payment_method', 'transaction_id', 'upi_ref',
            'status', 'paid_at', 'notes', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'company', 'recorded_by', 'created_at', 'updated_at']

    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None


class InvoiceListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'company', 'company_name',
            'billing_period_start', 'billing_period_end',
            'subtotal', 'total_amount', 'status', 'due_date',
            'sent_at', 'paid_at', 'created_at',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    amount_paid = serializers.SerializerMethodField()
    amount_due = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'company', 'company_name',
            'billing_period_start', 'billing_period_end',
            'line_items',
            'subtotal', 'cgst_rate', 'sgst_rate', 'igst_rate',
            'cgst_amount', 'sgst_amount', 'igst_amount', 'total_amount',
            'status', 'due_date', 'sent_at', 'paid_at',
            'pdf_file', 'notes',
            'amount_paid', 'amount_due',
            'payments',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number',
            'cgst_amount', 'sgst_amount', 'igst_amount', 'total_amount',
            'sent_at', 'paid_at', 'pdf_file',
            'created_at', 'updated_at',
        ]

    def get_amount_paid(self, obj):
        paid = sum(
            p.amount for p in obj.payments.all() if p.status == Payment.COMPLETED
        )
        return str(paid)

    def get_amount_due(self, obj):
        paid = sum(
            p.amount for p in obj.payments.all() if p.status == Payment.COMPLETED
        )
        return str(obj.total_amount - paid)


class CreateInvoiceSerializer(serializers.ModelSerializer):
    """For manually creating or editing a draft invoice."""

    class Meta:
        model = Invoice
        fields = [
            'company', 'billing_period_start', 'billing_period_end',
            'line_items', 'subtotal',
            'cgst_rate', 'sgst_rate', 'igst_rate',
            'due_date', 'notes',
        ]

    def validate_line_items(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError('At least one line item is required.')
        required = {'description', 'qty', 'rate'}
        for idx, item in enumerate(value):
            missing = required - set(item.keys())
            if missing:
                raise serializers.ValidationError(
                    f"Line item {idx + 1} is missing: {', '.join(missing)}"
                )
        return value

    def validate(self, attrs):
        if attrs['billing_period_start'] > attrs['billing_period_end']:
            raise serializers.ValidationError(
                {'billing_period_end': 'End date must be after start date.'}
            )
        return attrs

    def create(self, validated_data):
        period_start = validated_data['billing_period_start']
        validated_data['invoice_number'] = Invoice.generate_invoice_number(period_start)
        invoice = Invoice(**validated_data)
        invoice.compute_totals()
        invoice.save()
        return invoice

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.compute_totals()
        instance.save()
        return instance


class RecordPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'amount', 'payment_method', 'transaction_id', 'upi_ref',
            'paid_at', 'notes',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Payment amount must be greater than zero.')
        return value
