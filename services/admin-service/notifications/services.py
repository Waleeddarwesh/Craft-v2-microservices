from .models import Notification
from accounts.models import User
from .signals import notifications_created # Import our custom signal

def _get_ct_and_id(related_object):
    if related_object:
        return related_object._meta.model_name, related_object.id
    return None, None

def create_notification_for_user(user, message, related_object=None, image=None):
    """
    Creates a single notification. The 'post_save' signal will handle sending it.
    """
    if hasattr(user, 'notification_preferences') and not user.notification_preferences.in_app_notifications:
        return

    ct, obj_id = _get_ct_and_id(related_object)
    Notification.objects.create(
        user=user,
        message=message,
        content_type=ct,
        object_id=obj_id,
        image=image
    )

def create_notifications_for_all_suppliers(message, related_object=None, image=None):
    """
    Finds all supplier users, creates notifications in a single bulk query,
    and then fires a single signal to send them all.
    """
    suppliers = User.objects.filter(is_supplier=True)
    if not suppliers.exists():
        return

    ct, obj_id = _get_ct_and_id(related_object)
    notifications_to_create = []
    for supplier in suppliers:
        if hasattr(supplier, 'notification_preferences') and not supplier.notification_preferences.in_app_notifications:
            continue
        notifications_to_create.append(Notification(user=supplier, message=message, content_type=ct, object_id=obj_id, image=image))
        
    if not notifications_to_create:
        return
    
    created_notifications = Notification.objects.bulk_create(notifications_to_create)

    # Send our custom signal with the list of newly created notifications
    notifications_created.send(sender=None, notifications=created_notifications)

def create_notifications_for_all_users(message, related_object=None, image=None):
    """
    Creates a notification for every user in the system in a single bulk query
    and then fires a custom signal to broadcast them via WebSocket.
    """
    all_users = User.objects.all()
    if not all_users.exists():
        return

    ct, obj_id = _get_ct_and_id(related_object)
    notifications_to_create = []
    for user in all_users:
        if hasattr(user, 'notification_preferences') and not user.notification_preferences.in_app_notifications:
            continue
        notifications_to_create.append(Notification(user=user, message=message, content_type=ct, object_id=obj_id, image=image))
        
    if not notifications_to_create:
        return
    
    created_notifications = Notification.objects.bulk_create(notifications_to_create)

    # Send our custom signal to broadcast them
    notifications_created.send(sender=None, notifications=created_notifications)