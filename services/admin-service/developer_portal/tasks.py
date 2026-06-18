import logging
import time
import requests
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import WebhookDelivery
from .services import sign_webhook_payload

logger = logging.getLogger(__name__)

@shared_task
def send_webhook_delivery(delivery_id):
    """Sends webhook payload via Celery using requests and HMAC signing."""
    try:
        delivery = WebhookDelivery.objects.select_related('endpoint').get(id=delivery_id)
    except WebhookDelivery.DoesNotExist:
        logger.error(f"WebhookDelivery {delivery_id} not found.")
        return
        
    endpoint = delivery.endpoint
    if not endpoint.is_active:
        logger.info(f"WebhookEndpoint {endpoint.id} is inactive. Skipping delivery {delivery_id}.")
        return
        
    payload_str, signature = sign_webhook_payload(delivery.payload, endpoint.secret)
    
    headers = {
        'Content-Type': 'application/json',
        'X-Craft-Event': delivery.event,
        'X-Craft-Timestamp': str(int(time.time())),
        'X-Craft-Signature': signature,
    }
    
    delivery.attempts += 1
    
    try:
        response = requests.post(endpoint.url, data=payload_str, headers=headers, timeout=10)
        delivery.status_code = response.status_code
        delivery.response_body = response.text[:1000] # Limit to 1000 chars
        delivery.error_message = ""
        
        if 200 <= response.status_code < 300:
            delivery.success = True
            delivery.delivered_at = timezone.now()
            delivery.next_retry_at = None
        else:
            delivery.success = False
            
    except requests.RequestException as e:
        delivery.success = False
        delivery.error_message = str(e)[:1000]
        delivery.status_code = None
        
    if not delivery.success and delivery.attempts < 3:
        # Schedule retry with exponential backoff (5 min, 10 min, etc)
        delivery.next_retry_at = timezone.now() + timedelta(minutes=5 * delivery.attempts)
    elif not delivery.success:
        delivery.next_retry_at = None # Max retries reached
        
    delivery.save()

@shared_task
def retry_failed_webhooks():
    """Retries failed webhook deliveries where next_retry_at is <= now."""
    now = timezone.now()
    pending_deliveries = WebhookDelivery.objects.filter(
        success=False,
        next_retry_at__lte=now
    )
    for delivery in pending_deliveries:
        send_webhook_delivery.delay(delivery.id)
    
    logger.info(f"Scheduled {pending_deliveries.count()} webhooks for retry.")

@shared_task
def cleanup_old_webhook_deliveries():
    """Stub for cleaning up old webhook delivery logs."""
    logger.info("Task: cleanup_old_webhook_deliveries")

@shared_task
def expire_old_api_keys():
    """Stub for checking and deactivating expired API keys."""
    logger.info("Task: expire_old_api_keys")
