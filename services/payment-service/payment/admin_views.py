from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from craft_common.auth.permissions import HasRole
from returnrequest.models import BalanceWithdrawRequest, Transaction


class AdminWithdrawalsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        withdrawals = BalanceWithdrawRequest.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': str(w.id),
            'user_name': f"User {w.user_id}",
            'user': f"User {w.user_id}",
            'amount': float(w.amount),
            'transfer_type': w.transfer_type,
            'transfer_number': w.transfer_number,
            'transfer_status': w.transfer_status,
            'risk_score': float(w.risk_score) if w.risk_score else 0,
            'notes': w.notes or '',
            'admin_notes': w.admin_notes or '',
            'created_at': w.created_at,
        } for w in withdrawals]
        return Response(data)


class AdminWithdrawalActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def post(self, request, pk):
        try:
            w = BalanceWithdrawRequest.objects.get(pk=pk)
        except BalanceWithdrawRequest.DoesNotExist:
            return Response({"detail": "Withdrawal not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            w.transfer_status = 'Approved'
        elif action == 'reject':
            w.transfer_status = 'Rejected'
        else:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        w.admin_notes = request.data.get('notes', '')
        w.save(update_fields=['transfer_status', 'admin_notes'])
        return Response({"status": "success", "new_status": w.transfer_status})


class AdminPaymentsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        # Return empty list as payment records are external (Stripe)
        return Response([])


class AdminTransactionsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        transactions = Transaction.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': str(t.id),
            'transaction_type': t.transaction_type,
            'amount': float(t.amount),
            'user_email': f"User {t.user_id}",
            'user': f"User {t.user_id}",
            'created_at': t.created_at,
        } for t in transactions]
        return Response(data)
