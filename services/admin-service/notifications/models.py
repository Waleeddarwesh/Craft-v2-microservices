from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True, help_text="Target department if user is null")
    message = models.TextField()
    image = models.ImageField(upload_to='notifications/%Y/%m/%d/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Generic foreign key to link to any object (e.g., a ReturnRequest or an Order)
    content_type = models.CharField(max_length=255, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ("-timestamp",)

    @property
    def image_url(self):
        """
        Returns the URL of the image if it exists, otherwise None.
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    in_app_notifications = models.BooleanField(default=True, verbose_name="In-App Notifications")
    email_notifications = models.BooleanField(default=True, verbose_name="Email Notifications")
    push_notifications = models.BooleanField(default=True, verbose_name="Push Notifications")
    sms_notifications = models.BooleanField(default=False, verbose_name="SMS Notifications")

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Preferences for {self.user.email}"