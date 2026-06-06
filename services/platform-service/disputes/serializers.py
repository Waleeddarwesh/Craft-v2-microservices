from rest_framework import serializers
from .models import Dispute
from orders.models import Order
from returnrequest.models import ReturnRequest

class DisputeSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = Dispute
        fields = ['id', 'customer', 'customer_name', 'supplier', 'supplier_name', 'order', 'return_request', 'reason', 'status', 'admin_resolution', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'customer_name', 'supplier', 'supplier_name', 'status', 'admin_resolution', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        return obj.customer.get_full_name

    def get_supplier_name(self, obj):
        return obj.supplier.get_full_name

class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['order', 'return_request', 'reason']

    def validate(self, attrs):
        order = attrs.get('order')
        return_request = attrs.get('return_request')
        if not order and not return_request:
            raise serializers.ValidationError("Either 'order' or 'return_request' must be provided.")
        if order and return_request:
            raise serializers.ValidationError("Provide either 'order' or 'return_request', not both.")
        return attrs

class AdminDisputeResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['status', 'admin_resolution']
