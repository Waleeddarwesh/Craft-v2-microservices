from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "department", "is_read", "timestamp")
    list_filter = ("is_read", "timestamp", "department")
    search_fields = ("message", "user__email", "user__first_name")
    readonly_fields = ("timestamp",)
    fieldsets = (
        (None, {"fields": ("user", "department", "message", "is_read")}),
        ("Date Information", {"fields": ("timestamp",), "classes": ("collapse",)}),
    )
    ordering = ("-timestamp",)
    actions = ["mark_as_sent"]

    @admin.action(description="Mark selected notifications as sent")
    def mark_as_sent(self, request, queryset):
     queryset.update(sent=True)