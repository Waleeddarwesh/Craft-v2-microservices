from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets', verbose_name=_("User"))
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    description = models.TextField(verbose_name=_("Description"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name=_("Status"))
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, verbose_name=_("Priority"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Support Ticket")
        verbose_name_plural = _("Support Tickets")

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name=_("Ticket"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_messages', verbose_name=_("Sender"))
    message = models.TextField(verbose_name=_("Message"))
    attachment = models.FileField(upload_to='support_tickets/attachments/', null=True, blank=True, verbose_name=_("Attachment"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Ticket Message")
        verbose_name_plural = _("Ticket Messages")

    def __str__(self):
        return f"Message from {self.sender} on Ticket #{self.ticket_id}"
