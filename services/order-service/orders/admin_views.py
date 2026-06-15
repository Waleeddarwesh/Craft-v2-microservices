from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from craft_common.auth.permissions import HasRole
from orders.models import Order, Coupon
from returnrequest.models import ReturnRequest


class AdminOrdersView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': str(o.id),
            'order_number': o.order_number,
            'user_email': f"User {o.user_id}",
            'total_amount': float(o.total_amount),
            'discount_amount': float(o.discount_amount),
            'delivery_fee': float(o.delivery_fee),
            'final_amount': float(o.final_amount),
            'payment_method': o.payment_method,
            'status': o.status,
            'paid': o.paid,
            'created_at': o.created_at,
        } for o in orders]
        return Response(data)


class AdminReturnsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        returns = ReturnRequest.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': str(r.id),
            'order_id': str(r.order_id),
            'user_email': f"User {r.user_id}",
            'product_name': f"Product {r.product_id}",
            'status': r.status,
            'reason': r.reason,
            'amount': float(r.amount) if getattr(r, 'amount', None) else 0,
            'quantity': r.quantity,
            'created_at': r.created_at,
        } for r in returns]
        return Response(data)


class AdminReturnActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def post(self, request, pk):
        try:
            ret = ReturnRequest.objects.get(pk=pk)
        except ReturnRequest.DoesNotExist:
            return Response({"detail": "Return request not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            ret.status = 'accepted'
        elif action == 'reject':
            ret.status = 'rejected'
        else:
            return Response({"detail": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        ret.save(update_fields=['status'])
        return Response({"status": "success", "new_status": ret.status})


class AdminCouponsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        coupons = Coupon.objects.all().order_by('-id')[:100]
        data = [{
            'id': c.id,
            'code': c.code,
            'discount': float(c.discount),
            'discount_type': c.discount_type,
            'valid_from': c.valid_from,
            'valid_to': c.valid_to,
            'active': c.active,
            'min_purchase_amount': float(c.min_purchase_amount),
            'max_uses': c.max_uses,
            'uses_count': c.uses_count,
            'terms': c.terms,
        } for c in coupons]
        return Response(data)
