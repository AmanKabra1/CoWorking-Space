from django.contrib import admin
from .models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ['version_number', 'file_name', 'file_size', 'mime_type', 'uploaded_by', 'created_at']
    fields = ['version_number', 'file', 'file_name', 'file_size', 'mime_type', 'change_notes', 'uploaded_by', 'created_at']
    ordering = ['-version_number']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'doc_type', 'version_count', 'is_archived', 'uploaded_by', 'created_at']
    list_filter = ['doc_type', 'is_archived']
    search_fields = ['title', 'company__name', 'description']
    readonly_fields = ['uploaded_by', 'created_at', 'updated_at']
    inlines = [DocumentVersionInline]

    def version_count(self, obj):
        return obj.versions.count()
    version_count.short_description = 'Versions'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'file_name', 'file_size', 'mime_type', 'uploaded_by', 'created_at']
    list_filter = ['mime_type']
    search_fields = ['document__title', 'file_name']
    readonly_fields = ['version_number', 'file_name', 'file_size', 'mime_type', 'uploaded_by', 'created_at']
