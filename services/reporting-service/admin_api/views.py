"""
admin_api/views.py — Reporting Service
Cross-service imports removed:
  - REMOVED: all accounts.models imports (User, Supplier, Customer, Delivery, etc.)
  - REPLACED: craft_common.api_clients.auth_client for user/supplier counts
  - Reporting aggregations use local analytics data (AnalyticsAggregate model)
    populated by consuming domain events from the event bus.

This service is READ-ONLY for analytics. It never writes to other service DBs.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from craft_common.auth.permissions import HasRole
from craft_common.api_clients import auth_client  # internal HTTP client to auth-service

from .models import AnalyticsAggregate, DailyRevenueSummary, TopProduct


# ─── Dashboard Overview ──────────────────────────────────────────────────────

class DashboardOverviewView(APIView):
    """
    Returns high-level platform metrics for the admin dashboard.
    User/supplier counts are fetched from auth-service; revenue/order
    aggregates come from the local analytics DB.
    """
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        # Fetch user counts from auth-service (no direct accounts DB access)
        user_stats_response = auth_client.get("/internal/stats/user-counts/")
        user_stats = (
            user_stats_response.json()
            if user_stats_response.status_code == 200
            else {"total_users": None, "total_suppliers": None, "total_customers": None}
        )

        # Revenue and order aggregates come from local event-sourced data
        revenue = AnalyticsAggregate.objects.filter(
            metric_name="total_revenue", dimension="platform"
        ).order_by("-period").first()

        orders = AnalyticsAggregate.objects.filter(
            metric_name="order_count", dimension="platform"
        ).order_by("-period").first()

        return Response(
            {
                "user_counts": user_stats,
                "total_revenue": revenue.value if revenue else None,
                "total_orders":  orders.value  if orders  else None,
                "as_of_period":  revenue.period if revenue else None,
            }
        )


# ─── Revenue Reports ─────────────────────────────────────────────────────────

class RevenueReportView(APIView):
    """
    Returns daily/monthly revenue summaries built from order.paid events.
    No cross-service DB access — all data is local to reporting-service.
    """
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        period    = request.query_params.get("period", "daily")   # daily | monthly
        limit     = int(request.query_params.get("limit", 30))
        summaries = DailyRevenueSummary.objects.order_by("-date")[:limit]
        return Response(
            [
                {
                    "date":          str(s.date),
                    "gross_revenue": s.gross_revenue,
                    "order_count":   s.order_count,
                    "refund_amount": s.refund_amount,
                    "net_revenue":   s.net_revenue,
                }
                for s in summaries
            ]
        )


# ─── Top Products ─────────────────────────────────────────────────────────────

class TopProductsView(APIView):
    """
    Returns best-selling products. Product names are denormalized snapshots
    stored locally when product.created / product.updated events arrive.
    """
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        limit    = int(request.query_params.get("limit", 10))
        products = TopProduct.objects.order_by("-units_sold")[:limit]
        return Response(
            [
                {
                    "product_id":   p.product_id,
                    "product_name": p.product_name,  # denormalized
                    "units_sold":   p.units_sold,
                    "revenue":      p.revenue,
                }
                for p in products
            ]
        )


# ─── Supplier Analytics ───────────────────────────────────────────────────────

class SupplierAnalyticsView(APIView):
    """
    Returns per-supplier sales analytics.
    supplier_name is a denormalized snapshot updated via user.updated events.
    """
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        supplier_id = request.query_params.get("supplier_id")
        qs = AnalyticsAggregate.objects.filter(dimension="supplier")
        if supplier_id:
            qs = qs.filter(dimension_id=supplier_id)
        qs = qs.order_by("-period")[:50]

        return Response(
            [
                {
                    "supplier_id":   a.dimension_id,
                    "supplier_name": a.dimension_name,  # denormalized
                    "metric":        a.metric_name,
                    "value":         a.value,
                    "period":        a.period,
                }
                for a in qs
            ]
        )


# ─── System Health ────────────────────────────────────────────────────────────

class SystemHealthView(APIView):
    """
    Aggregate health check. Reporting-service only checks its own DB here.
    Full cross-service health is aggregated by the Traefik /health/ route.
    """
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        # Simple liveness check — if we can query, we're alive
        try:
            AnalyticsAggregate.objects.exists()
            db_ok = True
        except Exception:
            db_ok = False

        return Response(
            {"status": "ok" if db_ok else "degraded", "db": db_ok},
            status=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
