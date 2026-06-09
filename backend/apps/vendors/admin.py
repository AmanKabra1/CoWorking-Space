from django.contrib import admin
from .models import Vendor, VendorBill


class VendorBillInline(admin.TabularInline):
    model = VendorBill
    extra = 0
    fields = ['bill_number', 'bill_date', 'total_amount', 'status']
    readonly_fields = ['total_amount']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'building', 'contact_person', 'phone', 'is_active']
    list_filter = ['category', 'building', 'is_active']
    search_fields = ['name', 'contact_person', 'gst_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [VendorBillInline]


@admin.register(VendorBill)
class VendorBillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'vendor', 'building', 'bill_date', 'total_amount', 'status']
    list_filter = ['status', 'building', 'bill_date']
    search_fields = ['bill_number', 'description', 'vendor__name']
    readonly_fields = ['id', 'total_amount', 'created_at', 'updated_at']
