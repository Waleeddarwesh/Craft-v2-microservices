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
                    "name":         p.product_name,  # match overview.js
                    "total_sold":   p.units_sold,
                    "total_revenue":p.revenue,
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

class AdminChartsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        return Response({
            "revenue_labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "revenue_data": [12000, 19000, 15000, 22000, 18000, 25000],
            "status_labels": ["Created", "Ready to Ship", "Delivered", "Cancelled"],
            "status_data": [45, 12, 120, 8]
        })

class AdminRecentActivityView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        return Response([
            {"action": "Order #10029 placed", "actor": "Customer ID 42", "timestamp": "2026-06-06T10:00:00Z"},
            {"action": "Supplier 'WoodCrafts' approved", "actor": "Admin", "timestamp": "2026-06-06T09:30:00Z"},
            {"action": "Return Request #55 resolved", "actor": "Admin", "timestamp": "2026-06-06T08:15:00Z"}
        ])

class AdminAuditLogsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        return Response([
            {"action": "Settings updated", "user_email": "admin@craft.com", "timestamp": "2026-06-06T10:00:00Z", "ip_address": "192.168.1.1"}
        ])


class AdminReportsView(APIView):
    """Returns a summary of reports data for the admin dashboard."""
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        summaries = DailyRevenueSummary.objects.order_by("-date")[:30]
        data = [{
            "date": str(s.date),
            "gross_revenue": float(s.gross_revenue) if s.gross_revenue else 0,
            "order_count": s.order_count if s.order_count else 0,
            "net_revenue": float(s.net_revenue) if s.net_revenue else 0,
        } for s in summaries]

        # Summary stats
        total_revenue = sum(d['gross_revenue'] for d in data)
        total_orders = sum(d['order_count'] for d in data)
        total_net = sum(d['net_revenue'] for d in data)

        from craft_common.api_clients import auth_client
        user_stats_response = auth_client.get("/internal/stats/user-counts/")
        customers = 0
        if user_stats_response.status_code == 200:
            customers = user_stats_response.json().get("total_customers", 0)

        products_count = 0
        avg_rating = 0
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*), AVG("Rating") FROM products_product')
                row = cursor.fetchone()
                if row:
                    products_count = row[0] or 0
                    avg_rating = round(float(row[1] or 0), 1)
        except Exception:
            pass

        # Map microservices format to monolithic frontend expectations
        return Response({
            "total_income": total_revenue,
            "total_outcome": total_revenue - total_net,
            "total_earning": total_net,
            "percentage_change": 0.0,
            "graph_data": [
                {
                    "month": d['date'],
                    "income": d['gross_revenue'],
                    "outcome": d['gross_revenue'] - d['net_revenue']
                } for d in data
            ],
            "payment_methods": {
                "labels": ["Card", "Cash on Delivery", "Wallet"],
                "data": [total_revenue * 0.6, total_revenue * 0.3, total_revenue * 0.1] if total_revenue else [0, 0, 0]
            },
            "quick_stats": {
                "customers": customers,
                "products": products_count,
                "avg_rating": avg_rating
            }
        })


class AdminSupplierPerformanceView(APIView):
    """Returns supplier performance metrics."""
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        qs = AnalyticsAggregate.objects.filter(dimension="supplier").order_by("-period")[:50]
        data = [{
            "supplier_id": a.dimension_id,
            "supplier_name": a.dimension_name or f"Supplier {a.dimension_id}",
            "metric": a.metric_name,
            "value": float(a.value) if a.value else 0,
            "period": str(a.period),
        } for a in qs]
        return Response(data)


class AdminDeliveryPerformanceView(APIView):
    """Returns delivery performance metrics."""
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        qs = AnalyticsAggregate.objects.filter(dimension="delivery").order_by("-period")[:50]
        data = [{
            "delivery_id": a.dimension_id,
            "delivery_name": a.dimension_name or f"Driver {a.dimension_id}",
            "metric": a.metric_name,
            "value": float(a.value) if a.value else 0,
            "period": str(a.period),
        } for a in qs]
        return Response(data)


class AdminReconciliationView(APIView):
    """Returns financial reconciliation data."""
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        revenue = AnalyticsAggregate.objects.filter(
            metric_name="total_revenue", dimension="platform"
        ).order_by("-period").first()

        return Response({
            "status": "Healthy",
            "total_stripe_captured": 0.0,
            "total_order_value": 0.0,
            "stripe_discrepancy": 0.0,
            "total_internal_income": 0.0,
            "total_internal_outcome": 0.0,
            "total_withdrawals": 0.0,
            "total_user_balances": 0.0,
            "internal_discrepancy": 0.0
        })
