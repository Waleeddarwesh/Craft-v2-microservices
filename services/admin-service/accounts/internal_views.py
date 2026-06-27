from rest_framework import views, status, response
from rest_framework.permissions import BasePermission
from django.conf import settings
from .models import User

class IsInternalService(BasePermission):
    def has_permission(self, request, view):
        secret = request.headers.get('X-Internal-Secret')
        # In a real app, you would compare against a configured settings.INTERNAL_SERVICE_SECRET
        # For now, we will just assume any secret is fine if it exists, or match a simple env var
        expected_secret = getattr(settings, 'INTERNAL_SERVICE_SECRET', 'super-secret-internal-key')
        return secret == expected_secret

class InternalUserDetailView(views.APIView):
    permission_classes = [IsInternalService]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return response.Response({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": [r.name for r in user.roles.all()] if hasattr(user, 'roles') else [],
            })
        except User.DoesNotExist:
            return response.Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class InternalUserBulkLookupView(views.APIView):
    permission_classes = [IsInternalService]

    def post(self, request):
        ids = request.data.get('ids', [])
        users = User.objects.filter(id__in=ids)
        result = [
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": [r.name for r in user.roles.all()] if hasattr(user, 'roles') else [],
            }
            for user in users
        ]
        return response.Response(result)

class InternalUserFCMTokenView(views.APIView):
    permission_classes = [IsInternalService]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # Assuming FCM token is stored on the user model or a related profile
            fcm_token = getattr(user, 'fcm_token', None)
            return response.Response({"fcm_token": fcm_token})
        except User.DoesNotExist:
            return response.Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class InternalUserStatsView(views.APIView):
    permission_classes = [IsInternalService]
    def get(self, request):
        from accounts.models import User, Customer, Supplier
        return response.Response({
            'total_users': User.objects.count(),
            'total_customers': Customer.objects.count(),
            'total_suppliers': Supplier.objects.count()
        })

