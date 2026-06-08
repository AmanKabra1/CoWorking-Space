from rest_framework import serializers
from .models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_display = serializers.CharField(read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'version_number', 'file', 'file_url',
            'file_name', 'file_size', 'file_size_display', 'mime_type',
            'change_notes', 'uploaded_by', 'uploaded_by_name', 'created_at',
        ]
        read_only_fields = [
            'id', 'document', 'version_number', 'file_name', 'file_size',
            'mime_type', 'uploaded_by', 'created_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    latest_version = serializers.SerializerMethodField()
    version_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'company', 'company_name', 'title', 'description', 'doc_type',
            'tags', 'is_archived', 'uploaded_by', 'uploaded_by_name',
            'latest_version', 'version_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']

    def get_latest_version(self, obj):
        latest = obj.versions.order_by('-version_number').first()
        if latest:
            return DocumentVersionSerializer(latest, context=self.context).data
        return None

    def get_version_count(self, obj):
        return obj.versions.count()

    def validate_company(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and user.company != value:
            raise serializers.ValidationError(
                "You can only manage documents for your own company."
            )
        return value

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class UploadVersionSerializer(serializers.Serializer):
    file = serializers.FileField()
    change_notes = serializers.CharField(required=False, allow_blank=True, default='')
