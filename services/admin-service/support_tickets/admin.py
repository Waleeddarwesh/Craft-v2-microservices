from django.contrib import admin
from .models import Ticket, TicketMessage

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('subject', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TicketMessageInline]

    @admin.action(description="Mark selected tickets as Resolved")
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} tickets marked as Resolved.")

    @admin.action(description="Mark selected tickets as Closed")
    def mark_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} tickets marked as Closed.")

    actions = ['mark_resolved', 'mark_closed']

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ticket__id', 'sender__email', 'message')
    readonly_fields = ('created_at',)
