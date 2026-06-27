from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from craft_common.events import EventPublisher, schemas
from craft_common.auth.identity import identity_client
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

        user_data = {
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "roles": roles,
            "is_active": instance.is_active,
        }
        identity_client.set_user_details(instance.id, user_data)
            
        event = schemas.UserCreatedEvent(
            user_id=instance.id,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            roles=roles
        )
        publisher.publish(event)
    else:
        # Determine roles for updated user
        roles = []
        if instance.is_superuser or instance.is_staff:
            roles.append("admin")
        if getattr(instance, 'is_customer', False):
            roles.append("customer")
        if getattr(instance, 'is_supplier', False):
            roles.append("supplier")
        if getattr(instance, 'is_delivery', False):
            roles.append("delivery")

        user_data = {
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "roles": roles,
            "is_active": instance.is_active,
        }
        identity_client.set_user_details(instance.id, user_data)
        
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
    identity_client.delete_user_details(instance.id)
    event = schemas.UserDeletedEvent(user_id=instance.id)
    publisher.publish(event)
