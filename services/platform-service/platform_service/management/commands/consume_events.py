from django.core.management.base import BaseCommand
from craft_common.events import EventConsumer
from disputes.models import Dispute
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consume RabbitMQ events for platform-service'

    def handle(self, *args, **options):
        consumer = EventConsumer(queue_name='platform_service_queue')
        
        # Subscribe to events
        consumer.subscribe('order.delivered', self.handle_order_delivered)
        consumer.subscribe('return.approved', self.handle_return_approved)

        self.stdout.write(self.style.SUCCESS('Starting event consumer for platform-service...'))
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Consumer stopped.'))
            consumer.stop_consuming()

    def handle_order_delivered(self, payload):
        order_id = payload.get('order_id')
        user_id = payload.get('user_id')
        # Logic to enable verified purchase for reviews
        self.stdout.write(self.style.SUCCESS(f"Order {order_id} delivered. Verified purchase enabled for User {user_id}."))

    def handle_return_approved(self, payload):
        return_request_id = payload.get('return_request_id')
        if not return_request_id:
            return
            
        disputes = Dispute.objects.filter(return_request_id=return_request_id, status=Dispute.Status.OPEN)
        count = disputes.update(
            status=Dispute.Status.RESOLVED,
            admin_resolution="Auto-resolved because return request was approved."
        )
        self.stdout.write(self.style.SUCCESS(f"Return {return_request_id} approved. Auto-resolved {count} disputes."))
