from celery import shared_task
from django.shortcuts import get_object_or_404
from accounts.models import User
from .models import Conversation
from notifications.services import create_notification_for_user

@shared_task
def send_chat_notification_task(sender_id, recipient_id, message, conversation_id):
    """
    Asynchronously sends a notification with the sender's image.
    """
    try:
        recipient = User.objects.get(id=recipient_id)
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=conversation_id)
        sender_photo = None
        if sender.profile_picture:
            sender_photo = sender.profile_picture.url if hasattr(sender.profile_picture, 'url') else sender.profile_picture

        create_notification_for_user(
            user=recipient,
            message=message,
            related_object=conversation,
            image=sender_photo  
        )
    except (User.DoesNotExist, Conversation.DoesNotExist):
        print(f"Could not send notification for conversation {conversation_id}")