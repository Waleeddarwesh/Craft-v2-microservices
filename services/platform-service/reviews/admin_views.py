from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from craft_common.auth.permissions import HasRole

from disputes.models import Dispute
from support_tickets.models import Ticket, TicketMessage
from audit_logs.models import FraudAlert
from .models import Review

class AdminReviewsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        reviews = Review.objects.all().order_by('-id')[:100]
        data = [{
            'id': r.id,
            'product_id': r.product_id,
            'product_name': r.product_name,
            'course_id': r.course_id,
            'course_name': r.course_name,
            'user_id': r.user_id,
            'customer_name': r.user_name,
            'status': r.status,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        } for r in reviews]
        return Response(data)

class AdminReviewActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def post(self, request, pk):
        try:
            r = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        if action == "approve":
            r.status = Review.Status.APPROVED
        elif action == "reject":
            r.status = Review.Status.REJECTED
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        r.save(update_fields=['status'])
        return Response({"status": "success", "new_status": r.status})


class AdminDisputesView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        disputes = Dispute.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': d.id,
            'customer_id': d.customer_id,
            'supplier_id': d.supplier_id,
            'order_id': d.order_id,
            'status': d.status,
            'reason': d.reason,
            'created_at': d.created_at,
        } for d in disputes]
        return Response(data)


class AdminDisputeDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request, pk):
        try:
            d = Dispute.objects.get(pk=pk)
        except Dispute.DoesNotExist:
            return Response({"detail": "Dispute not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'id': d.id,
            'customer_id': d.customer_id,
            'supplier_id': d.supplier_id,
            'order_id': d.order_id,
            'status': d.status,
            'reason': d.reason,
            'admin_resolution': d.admin_resolution,
            'created_at': d.created_at,
        })

    def patch(self, request, pk):
        try:
            d = Dispute.objects.get(pk=pk)
        except Dispute.DoesNotExist:
            return Response({"detail": "Dispute not found"}, status=status.HTTP_404_NOT_FOUND)

        if 'status' in request.data:
            d.status = request.data['status']
        if 'admin_resolution' in request.data:
            d.admin_resolution = request.data['admin_resolution']
        
        d.save()
        return Response({"status": "success"})


class AdminSupportTicketsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        tickets = Ticket.objects.all().order_by('-id')[:100]
        data = [{
            'id': t.id,
            'user_id': t.user_id,
            'user_name': t.user_name,
            'subject': t.subject,
            'status': t.status,
            'priority': getattr(t, 'priority', 'medium'),
        } for t in tickets]
        return Response(data)


class AdminSupportTicketDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request, pk):
        try:
            t = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        messages = TicketMessage.objects.filter(ticket=t).order_by('created_at')
        msgs_data = []
        for m in messages:
            msgs_data.append({
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_name': m.sender_name,
                'message': m.message,
                'created_at': m.created_at,
                'is_admin': getattr(m, 'is_admin', False) # If no is_admin field
            })

        return Response({
            'id': t.id,
            'user_id': t.user_id,
            'user_name': t.user_name,
            'subject': t.subject,
            'description': t.description,
            'status': t.status,
            'messages': msgs_data
        })

    def post(self, request, pk):
        try:
            t = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        if action == "reply":
            msg = request.data.get("message")
            if msg:
                # Basic creation since no explicit is_admin field in model schema observed
                TicketMessage.objects.create(
                    ticket=t,
                    message=msg,
                    sender_id=request.user.id,
                    sender_name="Admin"
                )
            
        new_status = request.data.get("status")
        if new_status:
            t.status = new_status
            t.save()

        return Response({"status": "success"})


class AdminFraudAlertsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        alerts = FraudAlert.objects.all().order_by('-created_at')[:100]
        data = [{
            'id': a.id,
            'user_id': a.user_id,
            'reason': a.reason,
            'risk_score': a.risk_score,
            'status': a.status,
            'created_at': a.created_at,
        } for a in alerts]
        return Response(data)

class AdminFraudAlertActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def post(self, request, pk):
        try:
            a = FraudAlert.objects.get(pk=pk)
        except FraudAlert.DoesNotExist:
            return Response({"detail": "Fraud alert not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        if action == "resolve":
            a.status = FraudAlert.Status.RESOLVED
        elif action == "suspend":
            a.status = FraudAlert.Status.ACTION_TAKEN
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
        a.notes = request.data.get("notes", "")
        from django.utils import timezone
        a.resolved_at = timezone.now()
        a.save()
        return Response({"status": "success", "new_status": a.status})
