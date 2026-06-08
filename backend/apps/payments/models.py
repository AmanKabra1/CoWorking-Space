from django.db import models


class PaymentGateway(models.Model):
    RAZORPAY = 'razorpay'
    STRIPE = 'stripe'
    PROVIDER_CHOICES = [
        (RAZORPAY, 'Razorpay'),
        (STRIPE, 'Stripe'),
    ]

    company = models.OneToOneField(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='payment_gateway',
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'

    def __str__(self):
        return f"{self.company.name} — {self.get_provider_display()}"


class PaymentOrder(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    invoice = models.ForeignKey(
        'billing.Invoice',
        on_delete=models.CASCADE,
        related_name='payment_orders',
    )
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
    )
    provider = models.CharField(max_length=20)
    gateway_order_id = models.CharField(max_length=255, unique=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Order'
        verbose_name_plural = 'Payment Orders'

    def __str__(self):
        return f"{self.gateway_order_id} — {self.status}"
