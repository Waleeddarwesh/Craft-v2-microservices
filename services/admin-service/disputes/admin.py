from django.contrib import admin
from .models import Dispute

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'supplier', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__email', 'supplier__email', 'reason')
    readonly_fields = ('created_at', 'updated_at')
