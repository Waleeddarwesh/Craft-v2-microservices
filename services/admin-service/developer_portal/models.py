from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class APIService(models.Model):
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('outage', 'Outage')
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    version = models.CharField(max_length=20, default="v2.0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="healthy")
    description = models.CharField(max_length=255)
    schema_url = models.CharField(max_length=255)
    endpoint_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.version})"

class DeveloperAPIKey(models.Model):
    ENVIRONMENTS = [
        ("test", "Test"),
        ("live", "Live"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="developer_api_keys")
    name = models.CharField(max_length=100)

    key_prefix = models.CharField(max_length=20, unique=True, db_index=True)
    hashed_key = models.CharField(max_length=255)

    environment = models.CharField(max_length=20, choices=ENVIRONMENTS, default="test")
    scopes = models.JSONField(default=list)

    is_active = models.BooleanField(default=True)
    request_count = models.PositiveIntegerField(default=0)

    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "environment"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.environment})"

class ChangelogEntry(models.Model):
    TYPE_CHOICES = [
        ('feature', 'Feature'),
        ('fix', 'Fix'),
        ('deprecation', 'Deprecation'),
        ('announcement', 'Announcement')
    ]
    
    version = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='feature')
    published_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_date', '-id']
        
    def __str__(self):
        return f"{self.version} - {self.title}"

class WebhookEndpoint(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="webhook_endpoints")
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)

    events = models.JSONField(default=list)
    secret = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
        ]

    def __str__(self):
        return self.url

class WebhookDelivery(models.Model):
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")

    event = models.CharField(max_length=100)
    payload = models.JSONField()

    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    success = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    next_retry_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["success"]),
            models.Index(fields=["next_retry_at"]),
            models.Index(fields=["created_at"]),
        ]
