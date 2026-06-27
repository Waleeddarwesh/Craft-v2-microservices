import datetime
from rest_framework import serializers
from django.conf import settings
from .models import PaymentHistory, BalanceWithdrawRequest, Transaction

class OrderInformationSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()

    def validate_order_id(self, value):
        # Microservice validation would be an API call
        return value
    
class CourseInformationSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        # Microservice validation would be an API call
        return value

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'

class BalanceWithdrawRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    transfer_status = serializers.CharField(source='get_transfer_status_display', read_only=True)
    admin_notes = serializers.CharField(read_only=True)

    class Meta:
        model = BalanceWithdrawRequest
        fields = [
            'id', 'user', 'amount', 'transfer_number', 'transfer_type', 
            'notes', 'transfer_status', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'transfer_status', 'admin_notes', 
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'transfer_type': {'required': True},
            'transfer_number': {'required': True}
        }

    def validate_amount(self, value):
        from django.utils.translation import gettext_lazy as _
        if value <= 0:
            raise serializers.ValidationError(_("Withdrawal amount must be positive."))
        return value

class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'created_at']
