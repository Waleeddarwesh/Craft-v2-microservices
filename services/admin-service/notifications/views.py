from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for users to retrieve their notifications,
    or notifications targeting their department.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Get roles (which often map to departments in Craft RBAC)
        roles = []
        if hasattr(user, 'roles'):
            roles = [role.name for role in user.roles.all()]
            
        # Also map specific roles to departments explicitly if needed
        departments = roles[:]
        if 'admin' in roles or 'super_admin' in roles:
            departments.append('Admin')
        if 'support' in roles:
            departments.append('Support')
            
        return Notification.objects.filter(
            Q(user=user) | Q(department__in=departments)
        ).order_by('-timestamp')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        qs = self.get_queryset()
        qs.update(is_read=True)
        return Response({'status': 'all marked as read'})
