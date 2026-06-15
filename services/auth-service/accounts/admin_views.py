from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from craft_common.auth.permissions import HasRole
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminUsersView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        customers = []
        suppliers = []
        delivery = []
        
        users = User.objects.all().select_related('customer', 'supplier', 'delivery')[:500]
        
        for u in users:
            if u.is_supplier and hasattr(u, 'supplier'):
                s = u.supplier
                suppliers.append({
                    'id': u.id,
                    'user_id': u.id,
                    'email': u.email,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'name': f"{u.first_name} {u.last_name}",
                    'CategoryTitle': s.CategoryTitle,
                    'Rating': float(s.Rating) if s.Rating else 0.0,
                    'FollowersNo': s.FollowersNo,
                    'Orders': s.Orders or 0,
                    'accepted_supplier': s.accepted_supplier,
                })
            elif u.is_delivery and hasattr(u, 'delivery'):
                d = u.delivery
                delivery.append({
                    'id': u.id,
                    'user_id': u.id,
                    'email': u.email,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'name': f"{u.first_name} {u.last_name}",
                    'VehicleModel': getattr(d, 'VehicleModel', ''),
                    'plateNO': getattr(d, 'plateNO', ''),
                    'governorate': getattr(d, 'governorate', ''),
                    'Rating': float(getattr(d, 'Rating', 5.0)),
                    'accepted_delivery': getattr(d, 'accepted_delivery', False),
                })
            else:
                customers.append({
                    'id': u.id,
                    'user_id': u.id,
                    'email': u.email,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'full_name': f"{u.first_name} {u.last_name}",
                    'PhoneNO': u.PhoneNO,
                    'is_verified': u.is_verified,
                    'Balance': float(u.Balance),
                    'date_joined': str(u.date_joined),
                })

        return Response({
            'customers': customers,
            'suppliers': suppliers,
            'delivery': delivery
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request, pk):
        try:
            u = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'id': u.id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'full_name': f"{u.first_name} {u.last_name}",
            'is_active': u.is_active,
            'is_supplier': u.is_supplier,
            'is_delivery': u.is_delivery,
            'is_staff': u.is_staff,
            'is_customer': u.is_customer,
            'is_verified': getattr(u, 'is_verified', False),
            'date_joined': u.date_joined,
            'phone': getattr(u, 'PhoneNO', ''),
            'balance': float(getattr(u, 'Balance', 0.0)),
            'type': 'supplier' if u.is_supplier else ('delivery' if u.is_delivery else ('staff' if u.is_staff else 'customer')),
        }

        # Add supplier info if applicable
        if u.is_supplier:
            from accounts.models import Supplier
            try:
                s = Supplier.objects.get(user=u)
                data['supplier_info'] = {
                    'id': s.id,
                    'category': s.CategoryTitle,
                    'ExperienceYears': s.ExperienceYears,
                    'rating': float(s.Rating) if s.Rating else 0,
                    'orders': s.Orders,
                    'followers': s.FollowersNo,
                    'accepted': s.accepted_supplier,
                    'contract_url': s.Contract.url if s.Contract else '',
                    'identity_url': s.Identity.url if s.Identity else '',
                }
            except Supplier.DoesNotExist:
                data['supplier_info'] = None

        # Add delivery info if applicable
        if u.is_delivery:
            from accounts.models import Delivery
            try:
                d = Delivery.objects.get(user=u)
                data['delivery_info'] = {
                    'id': d.id,
                    'vehicle': d.VehicleModel,
                    'plate': d.plateNO,
                    'area': getattr(d, 'governorate', ''),
                    'rating': float(d.Rating) if d.Rating else 0,
                    'orders': d.Orders,
                    'accepted': getattr(d, 'accepted_delivery', False),
                    'contract_url': getattr(d.Contract, 'url', '') if getattr(d, 'Contract', None) else '',
                    'identity_url': getattr(d.Identity, 'url', '') if getattr(d, 'Identity', None) else '',
                }
            except Delivery.DoesNotExist:
                data['delivery_info'] = None

        return Response(data)


class AdminSupplierActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def patch(self, request, pk):
        from accounts.models import Supplier
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        accepted = request.data.get('accepted_supplier')
        if accepted is not None:
            supplier.accepted_supplier = accepted
            supplier.save(update_fields=['accepted_supplier'])

        return Response({"status": "success", "accepted_supplier": supplier.accepted_supplier})

    def delete(self, request, pk):
        from accounts.models import Supplier
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        supplier.accepted_supplier = False
        supplier.save(update_fields=['accepted_supplier'])
        return Response({"status": "success", "accepted_supplier": False})


class AdminDeliveryActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def patch(self, request, pk):
        from accounts.models import Delivery
        try:
            delivery = Delivery.objects.get(pk=pk)
        except Delivery.DoesNotExist:
            return Response({"detail": "Delivery person not found."}, status=status.HTTP_404_NOT_FOUND)

        accepted = request.data.get('accepted_delivery')
        if accepted is not None:
            delivery.accepted_delivery = accepted
            delivery.save(update_fields=['accepted_delivery'])

        return Response({"status": "success", "accepted_delivery": getattr(delivery, 'accepted_delivery', False)})

    def delete(self, request, pk):
        from accounts.models import Delivery
        try:
            delivery = Delivery.objects.get(pk=pk)
        except Delivery.DoesNotExist:
            return Response({"detail": "Delivery person not found."}, status=status.HTTP_404_NOT_FOUND)

        delivery.accepted_delivery = False
        delivery.save(update_fields=['accepted_delivery'])
        return Response({"status": "success", "accepted_delivery": False})


class AdminMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_staff or user.is_superuser:
            modules = [
                {"key": "overview"}, {"key": "orders"}, {"key": "returns"}, {"key": "products"},
                {"key": "users"}, {"key": "payments"}, {"key": "withdrawals"}, {"key": "coupons"},
                {"key": "reports"}, {"key": "supplier-performance"}, {"key": "delivery-performance"},
                {"key": "fraud-alerts"}, {"key": "support-tickets"}, {"key": "disputes"},
                {"key": "courses"}, {"key": "product-moderation"}, {"key": "reviews"},
                {"key": "notifications"}, {"key": "reconciliation"}, {"key": "audit-logs"},
                {"key": "settings"}
            ]
            widgets = [
                "revenue_chart", "status_chart", "total_orders", "active_users",
                "total_revenue", "pending_returns", "products_in_stock", "pending_withdrawals"
            ]
        else:
            modules = []
            widgets = []

        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "modules": modules,
            "widgets": widgets
        })
