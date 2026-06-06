from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def get_client_ip(request):
    """Retrieve the client's IP address from a Django request."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit_action(user, action, instance=None, old_value=None, new_value=None, request=None):
    """
    Log an action in the Audit Logs.
    
    :param user: The User who performed the action.
    :param action: A string describing the action (e.g. 'Admin approved supplier').
    :param instance: The object that was modified/acted upon.
    :param old_value: Dict representing the old state of the object.
    :param new_value: Dict representing the new state of the object.
    :param request: The HTTP request (used to extract IP and UserAgent).
    """
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:512]

    content_type = None
    object_id = None
    
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        object_id = str(instance.pk)

    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=object_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent
    )
