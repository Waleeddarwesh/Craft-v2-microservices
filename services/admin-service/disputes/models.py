from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Dispute(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        INVESTIGATING = 'investigating', _('Investigating')
        RESOLVED_CUSTOMER = 'resolved_customer', _('Resolved (Customer Win)')
        RESOLVED_SUPPLIER = 'resolved_supplier', _('Resolved (Supplier Win)')
        CLOSED = 'closed', _('Closed')

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_disputes', verbose_name=_("Customer"))
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_disputes', verbose_name=_("Supplier"))
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='disputes', verbose_name=_("Order"))
    return_request = models.ForeignKey('returnrequest.ReturnRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='disputes', verbose_name=_("Return Request"))
    
    reason = models.TextField(verbose_name=_("Reason for Dispute"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name=_("Status"))
    admin_resolution = models.TextField(null=True, blank=True, verbose_name=_("Admin Resolution"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Dispute")
        verbose_name_plural = _("Disputes")

    def __str__(self):
        return f"Dispute #{self.id} - {self.customer} vs {self.supplier}"
