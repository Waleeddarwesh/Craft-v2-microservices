from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from craft_common.events import EventPublisher, schemas
from .models import User

publisher = EventPublisher()

@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    if created:
        roles = []
        if instance.is_superuser or instance.is_staff:
            roles.append("admin")
        if getattr(instance, 'is_customer', False):
            roles.append("customer")
        if getattr(instance, 'is_supplier', False):
            roles.append("supplier")
        if getattr(instance, 'is_delivery', False):
            roles.append("delivery")
            
        event = schemas.UserCreatedEvent(
            user_id=instance.id,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            roles=roles
        )
        publisher.publish(event)
    else:
        event = schemas.UserUpdatedEvent(
            user_id=instance.id,
            data={
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name
            }
        )
        publisher.publish(event)

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    event = schemas.UserDeletedEvent(user_id=instance.id)
    publisher.publish(event)
