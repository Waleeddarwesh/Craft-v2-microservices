import logging

logger = logging.getLogger(__name__)

def send_push_notification(fcm_token, title, body, data=None):
    """
    Stub service to send push notification via FCM.
    In a real environment, you'd use firebase_admin.messaging.
    """
    if not fcm_token:
        return
        
    # Stub: just log the notification
    logger.info(f"FCM PUSH NOTIFICATION SENT TO {fcm_token}: {title} - {body}")
