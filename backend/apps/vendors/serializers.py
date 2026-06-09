from rest_framework import serializers
from .models import Vendor, VendorBill


class VendorSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    bill_count = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'category', 'category_display',
            'building', 'building_name',
            'contact_person', 'email', 'phone', 'gst_number',
            'address', 'notes', 'is_active', 'bill_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_bill_count(self, obj):
        return obj.bills.count()


class VendorBillSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VendorBill
        fields = [
            'id', 'vendor', 'vendor_name', 'building', 'building_name',
            'bill_number', 'bill_date', 'due_date',
            'amount', 'tax_amount', 'total_amount',
            'status', 'status_display', 'paid_at',
            'description', 'attachment', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

    def validate(self, attrs):
        amount = attrs.get('amount', getattr(self.instance, 'amount', 0))
        tax = attrs.get('tax_amount', getattr(self.instance, 'tax_amount', 0))
        if amount is not None and amount < 0:
            raise serializers.ValidationError({'amount': 'Amount cannot be negative.'})
        if tax is not None and tax < 0:
            raise serializers.ValidationError({'tax_amount': 'Tax cannot be negative.'})
        return attrs

    def create(self, validated_data):
        bill = VendorBill(**validated_data)
        bill.compute_total()
        bill.save()
        return bill

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.compute_total()
        instance.save()
        return instance
