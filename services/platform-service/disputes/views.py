from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext as _
from rest_framework.filters import SearchFilter
from .models import Dispute
from .serializers import (
    DisputeSerializer, 
    DisputeCreateSerializer, 
    AdminDisputeResolveSerializer
)
from admin_api.permissions import require_permission
from notifications.services import create_notification_for_user

class DisputeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['reason', 'customer__email', 'supplier__email', 'order__order_number']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Dispute.objects.none()
            
        if user.is_staff and user.has_perm('accounts.can_manage_disputes'):
            return Dispute.objects.all()
            
        if hasattr(user, 'supplier'):
            return Dispute.objects.filter(supplier=user)
        return Dispute.objects.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return DisputeCreateSerializer
        return DisputeSerializer

    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')
        return_request = serializer.validated_data.get('return_request')
        
        supplier_user = None
        if order:
            supplier_user = order.items.first().product.Supplier.user
        elif return_request:
            supplier_user = return_request.supplier.user

        dispute = serializer.save(customer=self.request.user, supplier=supplier_user)

        # Notify supplier
        create_notification_for_user(
            user=supplier_user,
            message=_("A dispute has been opened against you regarding order/return #{id}.").format(id=order.id if order else return_request.id),
            related_object=dispute
        )
        # Notify customer
        create_notification_for_user(
            user=self.request.user,
            message=_("Your dispute has been successfully submitted and is under review."),
            related_object=dispute
        )

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser, require_permission('accounts.can_manage_disputes')])
    def resolve(self, request, pk=None):
        """Admin endpoint to resolve a dispute."""
        dispute = self.get_object()
        serializer = AdminDisputeResolveSerializer(dispute, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            if dispute.status == Dispute.Status.RESOLVED:
                # Notify customer
                create_notification_for_user(
                    user=dispute.customer,
                    message=_("Your dispute #{id} has been resolved. Resolution: {res}").format(id=dispute.id, res=dispute.admin_resolution),
                    related_object=dispute
                )
                # Notify supplier
                create_notification_for_user(
                    user=dispute.supplier,
                    message=_("Dispute #{id} has been resolved by an admin. Resolution: {res}").format(id=dispute.id, res=dispute.admin_resolution),
                    related_object=dispute
                )
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
