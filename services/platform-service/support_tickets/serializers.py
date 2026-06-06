from rest_framework import serializers
from .models import Ticket, TicketMessage

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = ['id', 'sender', 'sender_name', 'message', 'attachment', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_name', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name

class TicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'user', 'user_name', 'subject', 'description', 'status', 'priority', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'user', 'user_name', 'status', 'created_at', 'updated_at', 'messages']

    def get_user_name(self, obj):
        return obj.user.get_full_name

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'priority']

class AdminTicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority']
