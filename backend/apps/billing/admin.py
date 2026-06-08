from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['id', 'amount', 'payment_method', 'transaction_id', 'status', 'paid_at', 'recorded_by']
    fields = ['amount', 'payment_method', 'transaction_id', 'upi_ref', 'status', 'paid_at', 'recorded_by']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'company', 'billing_period_start', 'billing_period_end',
        'subtotal', 'total_amount', 'status_badge', 'due_date',
    ]
    list_filter = ['status', 'billing_period_start', 'company']
    search_fields = ['invoice_number', 'company__name']
    readonly_fields = [
        'id', 'invoice_number', 'cgst_amount', 'sgst_amount', 'igst_amount',
        'total_amount', 'sent_at', 'paid_at', 'created_at', 'updated_at',
    ]
    ordering = ['-billing_period_start']
    inlines = [PaymentInline]

    fieldsets = (
        (None, {'fields': ('id', 'invoice_number', 'company', 'status')}),
        ('Period', {'fields': ('billing_period_start', 'billing_period_end', 'due_date')}),
        ('Line Items', {'fields': ('line_items',)}),
        ('Amounts', {'fields': (
            'subtotal',
            ('cgst_rate', 'cgst_amount'),
            ('sgst_rate', 'sgst_amount'),
            ('igst_rate', 'igst_amount'),
            'total_amount',
        )}),
        ('Delivery', {'fields': ('pdf_file', 'sent_at', 'paid_at')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'draft': '#6b7280', 'sent': '#2563eb', 'paid': '#16a34a',
            'overdue': '#dc2626', 'cancelled': '#9ca3af',
        }
        colour = colours.get(obj.status, '#374151')
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            colour, obj.get_status_display(),
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'invoice', 'company', 'amount', 'payment_method', 'status', 'paid_at', 'recorded_by',
    ]
    list_filter = ['status', 'payment_method', 'company']
    search_fields = ['invoice__invoice_number', 'transaction_id', 'upi_ref', 'company__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-paid_at']
