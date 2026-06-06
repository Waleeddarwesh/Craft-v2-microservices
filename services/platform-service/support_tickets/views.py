from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext as _
from rest_framework.filters import SearchFilter
from .models import Ticket, TicketMessage
from .serializers import (
    TicketSerializer, 
    TicketCreateSerializer, 
    TicketMessageSerializer, 
    AdminTicketUpdateSerializer
)
from admin_api.permissions import require_permission

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['subject', 'description', 'user__email']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Ticket.objects.none()
            
        if user.is_staff and user.has_perm('accounts.can_manage_support_tickets'):
            return Ticket.objects.all()
        return Ticket.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        
        # Only allow reply if ticket is open or in progress, unless it's an admin closing it
        if ticket.status == Ticket.Status.CLOSED and not request.user.is_staff:
            return Response({'error': _("Cannot reply to a closed ticket.")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TicketMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, sender=request.user)
            
            # If admin replies, change status to In Progress
            if request.user.is_staff and ticket.status == Ticket.Status.OPEN:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.save(update_fields=['status'])
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser, require_permission('accounts.can_manage_support_tickets')])
    def manage(self, request, pk=None):
        """Admin endpoint to update ticket status/priority."""
        ticket = self.get_object()
        serializer = AdminTicketUpdateSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
