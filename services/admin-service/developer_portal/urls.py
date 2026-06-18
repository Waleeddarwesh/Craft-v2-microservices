from django.urls import path
from . import views

urlpatterns = [
    path("", views.overview, name="developer-root"),
    path("overview/", views.overview, name="developer-overview"),
    path("getting-started/", views.getting_started, name="developer-getting-started"),
    path("catalog/", views.api_catalog, name="developer-catalog"),
    path("explorer/", views.api_explorer, name="developer-explorer"),
    path("authentication/", views.authentication, name="developer-authentication"),
    
    # API Keys
    path("api-keys/", views.api_keys_page, name="developer-api-keys"),
    path("api-keys/create/", views.create_api_key_view, name="developer-api-key-create"),
    path("api-keys/<int:pk>/revoke/", views.revoke_api_key_view, name="developer-api-key-revoke"),

    # Webhooks
    path("webhooks/", views.webhooks_page, name="developer-webhooks"),
    path("webhooks/create/", views.create_webhook_view, name="developer-webhook-create"),
    path("webhooks/<int:pk>/delete/", views.delete_webhook_view, name="developer-webhook-delete"),
    path("webhooks/<int:pk>/test/", views.test_webhook_view, name="developer-webhook-test"),

    path("status/", views.api_status, name="developer-status"),
    path("changelog/", views.changelog, name="developer-changelog"),
]
