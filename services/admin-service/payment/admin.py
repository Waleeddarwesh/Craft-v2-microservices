from django.contrib import admin
from .models import PaymentHistory

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'payment_status', 'stripe_payment_intent_id', 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'order__order_number', 'stripe_payment_intent_id')
    list_filter = ('payment_status', 'date')
    ordering = ('-date',)
    readonly_fields = ('stripe_session_id', 'stripe_payment_intent_id')