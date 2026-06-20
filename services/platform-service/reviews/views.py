"""
reviews/views.py — Platform Service
Cross-service imports removed:
  - REMOVED: from accounts.permissions import IsAuthenticated
  - REMOVED: from accounts.models import Delivery, Supplier, Customer
  - REPLACED: DRF standard IsAuthenticated + craft_common HasRole

User identity (user_id, roles) comes from JWT headers injected by Traefik.
Supplier/customer/delivery distinction is expressed through the user's role
from the JWT payload — no accounts DB lookup needed.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated  # DRF standard — not accounts.permissions
from rest_framework.response import Response

from craft_common.auth.permissions import HasRole
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class  = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Review.objects.all()

        # Filter by reviewable entity
        product_id = self.request.query_params.get("product_id")
        course_id  = self.request.query_params.get("course_id")
        if product_id:
            qs = qs.filter(product_id=product_id)
        if course_id:
            qs = qs.filter(course_id=course_id)

        return qs.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """
        Submit a review. The reviewer's role is read from the JWT header
        (X-User-Roles injected by Traefik) — no Delivery/Supplier model needed.

        Verified-purchase flag is set by the event consumer when order.delivered fires.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(
            user_id=request.user.id,
            user_name=request.headers.get("X-User-Name", "Unknown User"),  # denormalized from JWT header
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[HasRole("admin")])
    def approve(self, request, pk=None):
        """Approve a review and publish review.approved event."""
        review = self.get_object()
        review.status = "APPROVED"
        review.save(update_fields=["status"])

        # Publish event so catalog-service can recalculate rating
        from craft_common.events.publisher import EventPublisher
        from craft_common.events.schemas import ReviewApprovedEvent
        EventPublisher().publish(
            ReviewApprovedEvent(
                review_id=review.id,
                product_id=review.product_id,
                rating=review.rating,
            )
        )

        return Response({"detail": "Review approved."})

    @action(detail=True, methods=["post"], permission_classes=[HasRole("admin")])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.status = "REJECTED"
        review.save(update_fields=["status"])
        return Response({"detail": "Review rejected."})

    @action(detail=False, methods=["get"])
    def my_reviews(self, request):
        """Return reviews submitted by the currently authenticated user."""
        reviews = Review.objects.filter(user_id=request.user.id).order_by("-created_at")
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
