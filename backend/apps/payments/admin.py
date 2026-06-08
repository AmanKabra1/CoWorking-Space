from django.contrib import admin

from .models import PaymentGateway, PaymentOrder


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['company', 'provider', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['company__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['gateway_order_id', 'invoice', 'provider', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['provider', 'status']
    search_fields = ['gateway_order_id', 'gateway_payment_id', 'invoice__invoice_number']
    readonly_fields = ['created_at', 'updated_at']
