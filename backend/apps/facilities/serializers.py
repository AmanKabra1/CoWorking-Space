from rest_framework import serializers
from .models import Facility, FacilityImage


class _RatingMixin(serializers.Serializer):
    """Adds avg_rating + review_count from the facility's booking reviews."""
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_avg_rating(self, obj):
        ratings = list(obj.reviews.values_list('rating', flat=True))
        return round(sum(ratings) / len(ratings), 1) if ratings else None


class FacilityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order']
        read_only_fields = ['id']


class FacilityListSerializer(_RatingMixin, serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'building', 'building_name',
            'floor', 'floor_name', 'capacity', 'price_per_hour', 'price_per_day',
            'is_active', 'is_public', 'owner_company', 'description',
            'image_url', 'primary_image',
            'avg_rating', 'review_count',
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        # Fall back to a hosted image URL when no file was uploaded.
        return obj.image_url or None


class FacilitySerializer(_RatingMixin, serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    owner_company_name = serializers.CharField(source='owner_company.name', read_only=True, default=None)
    images = FacilityImageSerializer(many=True, read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type',
            'building', 'building_name', 'floor', 'floor_name',
            'owner_company', 'owner_company_name',
            'capacity', 'price_per_hour', 'price_per_day',
            'description', 'image_url', 'amenities', 'booking_rules',
            'images', 'is_active', 'is_public', 'avg_rating', 'review_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner_company', 'created_at', 'updated_at']


class AddFacilityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityImage
        fields = ['image', 'caption', 'is_primary', 'order']
