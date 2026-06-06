from django.db import models
from django.utils.translation import gettext_lazy as _

class AuditLog(models.Model):
    user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Actor User ID")
    )
    action = models.CharField(max_length=255, verbose_name=_("Action"))
    
    # Replaced Generic Relation with plain strings for cross-service compatibility
    entity_type = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Entity Type"))
    entity_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Entity ID"))
    
    old_value = models.JSONField(null=True, blank=True, verbose_name=_("Old Value"))
    new_value = models.JSONField(null=True, blank=True, verbose_name=_("New Value"))
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    user_agent = models.CharField(max_length=512, null=True, blank=True, verbose_name=_("User Agent"))
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user_id']),
        ]

    def __str__(self):
        return f"User {self.user_id} - {self.action} on {self.timestamp}"


class FraudAlert(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Review')
        INVESTIGATING = 'investigating', _('Investigating')
        RESOLVED = 'resolved', _('Resolved (Safe)')
        ACTION_TAKEN = 'action_taken', _('Action Taken (Suspended)')

    user_id = models.BigIntegerField(verbose_name=_("User ID"))
    reason = models.CharField(max_length=255, verbose_name=_("Trigger Reason"))
    risk_score = models.IntegerField(default=50) # 0-100
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by_id = models.BigIntegerField(null=True, blank=True, verbose_name=_("Resolved By Admin ID"))
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Fraud Alert for User {self.user_id} - {self.status}"
