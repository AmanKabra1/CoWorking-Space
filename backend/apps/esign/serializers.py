from rest_framework import serializers
from apps.esign.models import SignatureRequest, SignatureRecord


class SignatureRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatureRecord
        fields = [
            'id', 'request', 'signer', 'signer_email', 'signer_name',
            'order', 'status', 'signed_at', 'decline_reason', 'created_at',
        ]
        read_only_fields = ['id', 'signing_token', 'status', 'signed_at', 'created_at']


class SignatureRecordCreateSerializer(serializers.Serializer):
    signer_email = serializers.EmailField()
    signer_name = serializers.CharField(max_length=150)
    order = serializers.IntegerField(default=0)


class SignatureRequestSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    records = SignatureRecordSerializer(many=True, read_only=True)
    signers = SignatureRecordCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = SignatureRequest
        fields = [
            'id', 'title', 'document_file', 'message', 'created_by', 'created_by_name',
            'company', 'company_name', 'status', 'expires_at', 'certificate_file',
            'records', 'signers', 'created_at',
        ]
        read_only_fields = [
            'id', 'created_by', 'created_by_name', 'company', 'company_name',
            'status', 'certificate_file', 'records', 'created_at',
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.email

    def create(self, validated_data):
        signers_data = validated_data.pop('signers', [])
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['company'] = user.company
        validated_data['status'] = SignatureRequest.PENDING if signers_data else SignatureRequest.DRAFT

        req = SignatureRequest.objects.create(**validated_data)
        for signer in signers_data:
            SignatureRecord.objects.create(request=req, **signer)
        return req


class SignActionSerializer(serializers.Serializer):
    signature_data = serializers.CharField()


class DeclineActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
