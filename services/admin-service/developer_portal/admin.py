from django.contrib import admin
from .models import DeveloperAPIKey, WebhookEndpoint, WebhookDelivery, ChangelogEntry, APIService

@admin.register(APIService)
class APIServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'status', 'is_active')
    list_filter = ('status', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DeveloperAPIKey)
class DeveloperAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'environment', 'key_prefix', 'is_active', 'created_at')
    list_filter = ('environment', 'is_active')
    search_fields = ('name', 'owner__email', 'key_prefix')
    readonly_fields = ('hashed_key', 'key_prefix', 'request_count', 'last_used_at', 'created_at', 'revoked_at')

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('url', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('url', 'owner__email')
    readonly_fields = ('secret', 'created_at', 'updated_at')

@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'event', 'status_code', 'success', 'created_at')
    list_filter = ('success', 'event')
    search_fields = ('endpoint__url',)
    readonly_fields = ('endpoint', 'event', 'payload', 'status_code', 'response_body', 'error_message', 'success', 'attempts', 'next_retry_at', 'delivered_at', 'created_at')

@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'entry_type', 'published_date')
    list_filter = ('entry_type',)
    search_fields = ('title', 'description')
