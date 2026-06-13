from rest_framework import serializers
from django.utils.text import slugify
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'email', 'phone',
            'gst_number', 'pan_number', 'address', 'city', 'state', 'pincode',
            'logo', 'website', 'status', 'contract_start', 'contract_end',
            'notes', 'join_code', 'employee_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'join_code', 'employee_count', 'created_at', 'updated_at']

    def get_employee_count(self, obj):
        return obj.employee_count

    def validate_name(self, value):
        slug = slugify(value)
        qs = Company.objects.filter(slug=slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A company with this name already exists.')
        return value

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().update(instance, validated_data)


class CompanyListSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'email', 'phone',
            'city', 'state', 'status', 'employee_count', 'created_at',
        ]

    def get_employee_count(self, obj):
        return obj.employee_count
