from rest_framework import serializers
from .models import Facility, FacilityImage


class FacilityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order']
        read_only_fields = ['id']


class FacilityListSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'building', 'building_name',
            'floor', 'floor_name', 'capacity', 'price_per_hour', 'price_per_day',
            'is_active', 'primary_image',
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None


class FacilitySerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    images = FacilityImageSerializer(many=True, read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type',
            'building', 'building_name', 'floor', 'floor_name',
            'capacity', 'price_per_hour', 'price_per_day',
            'description', 'amenities', 'booking_rules',
            'images', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddFacilityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityImage
        fields = ['image', 'caption', 'is_primary', 'order']
