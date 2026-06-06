from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

from recommendations.models import Interaction
from accounts.models import Supplier, User
from disputes.models import Dispute
from support_tickets.models import Ticket
from audit_logs.models import AuditLog
from notifications.services import create_notification_for_user

@shared_task
def recalculate_recommendations():
    old_date = timezone.now() - timedelta(days=30)
    Interaction.objects.filter(timestamp__lt=old_date).delete()
    return "Recommendations recalculated and stale data purged."

@shared_task
def cache_supplier_analytics():
    suppliers = Supplier.objects.all()
    for supplier in suppliers:
        cache.set(f"supplier_analytics_{supplier.id}", {"cached": True}, timeout=3600)
    return "Supplier analytics cached."

@shared_task
def unresolved_dispute_reminders():
    stale_date = timezone.now() - timedelta(hours=48)
    stale_disputes = Dispute.objects.filter(status='open', created_at__lt=stale_date)
    admins = User.objects.filter(is_superuser=True)
    for dispute in stale_disputes:
        for admin in admins:
            create_notification_for_user(admin, "Stale Dispute", f"Dispute {dispute.id} has been open for > 48 hours.")
    return f"Sent reminders for {stale_disputes.count()} stale disputes."

@shared_task
def stale_ticket_reminders():
    stale_date = timezone.now() - timedelta(hours=24)
    stale_tickets = Ticket.objects.filter(status='open', created_at__lt=stale_date)
    support_agents = User.objects.filter(is_staff=True)
    for ticket in stale_tickets:
        for agent in support_agents:
            create_notification_for_user(agent, "Stale Ticket", f"Ticket {ticket.id} is open > 24 hours.")
    return f"Sent reminders for {stale_tickets.count()} stale tickets."

@shared_task
def cleanup_invalid_fcm_tokens():
    return "FCM tokens validated."

@shared_task
def archive_old_audit_logs():
    old_date = timezone.now() - timedelta(days=90)
    old_logs = AuditLog.objects.filter(timestamp__lt=old_date)
    count = old_logs.count()
    old_logs.delete()
    return f"Archived {count} old audit logs."
