from django.db import models
from django.utils.translation import gettext_lazy as _

class Dispute(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    customer_id = models.BigIntegerField(verbose_name=_("Customer ID"))
    supplier_id = models.BigIntegerField(verbose_name=_("Supplier ID"))
    
    order_id = models.UUIDField(null=True, blank=True, verbose_name=_("Order ID"))
    return_request_id = models.UUIDField(null=True, blank=True, verbose_name=_("Return Request ID"))
    
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
        return f"Dispute #{self.id} - Customer {self.customer_id} vs Supplier {self.supplier_id}"
