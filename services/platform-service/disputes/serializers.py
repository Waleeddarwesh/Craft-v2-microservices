from rest_framework import serializers
from .models import Dispute

class DisputeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dispute
        fields = ['id', 'customer_id', 'supplier_id', 'order_id', 'return_request_id', 'reason', 'status', 'admin_resolution', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_id', 'supplier_id', 'status', 'admin_resolution', 'created_at', 'updated_at']

class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['order_id', 'return_request_id', 'reason']

    def validate(self, attrs):
        order = attrs.get('order_id')
        return_request = attrs.get('return_request_id')
        if not order and not return_request:
            raise serializers.ValidationError("Either 'order_id' or 'return_request_id' must be provided.")
        if order and return_request:
            raise serializers.ValidationError("Provide either 'order_id' or 'return_request_id', not both.")
        return attrs

class AdminDisputeResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['status', 'admin_resolution']
