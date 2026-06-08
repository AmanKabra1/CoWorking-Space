from django.contrib import admin
from apps.esign.models import SignatureRequest, SignatureRecord


class SignatureRecordInline(admin.TabularInline):
    model = SignatureRecord
    extra = 0
    readonly_fields = ['signing_token', 'status', 'signed_at', 'ip_address']


@admin.register(SignatureRequest)
class SignatureRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'company', 'status', 'expires_at', 'created_at']
    list_filter = ['status']
    search_fields = ['title']
    inlines = [SignatureRecordInline]


@admin.register(SignatureRecord)
class SignatureRecordAdmin(admin.ModelAdmin):
    list_display = ['signer_name', 'signer_email', 'request', 'status', 'signed_at']
    list_filter = ['status']
    readonly_fields = ['signing_token']
