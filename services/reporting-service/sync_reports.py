import os
import django
from django.db import connection
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reporting_service.settings')
django.setup()

from admin_api.models import DailyRevenueSummary, AnalyticsAggregate, TopProduct

def sync_reports():
    print("Clearing existing reporting data...")
    DailyRevenueSummary.objects.all().delete()
    AnalyticsAggregate.objects.all().delete()
    TopProduct.objects.all().delete()

    print("Fetching existing orders from craft_db...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE(created_at), COUNT(*), SUM(total_amount), SUM(delivery_fee)
            FROM orders_order
            GROUP BY DATE(created_at)
        """)
        rows = cursor.fetchall()
        
        total_revenue = 0
        total_orders_global = 0

        for row in rows:
            order_date, count, total_amount, shipping_fee = row
            # For simplicity, let's treat total_amount as gross revenue
            gross_revenue = float(total_amount or 0)
            net_revenue = gross_revenue - float(shipping_fee or 0)
            
            DailyRevenueSummary.objects.create(
                date=order_date,
                gross_revenue=gross_revenue,
                order_count=count,
                refund_amount=0.0,
                net_revenue=net_revenue
            )
            total_revenue += gross_revenue
            total_orders_global += count

    print(f"Created {len(rows)} daily revenue summaries.")

    # Create total_revenue aggregate
    AnalyticsAggregate.objects.create(
        metric_name="total_revenue",
        dimension="platform",
        value=total_revenue,
        period=str(date.today().replace(day=1)) # Just an approximation for monthly/total
    )

    AnalyticsAggregate.objects.create(
        metric_name="order_count",
        dimension="platform",
        value=total_orders_global,
        period=str(date.today().replace(day=1))
    )

    # Sync top products
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p."ProductName", SUM(oi.quantity), SUM(oi.price * oi.quantity)
                FROM orders_orderitem oi
                JOIN products_product p ON p.id = oi.product_id
                GROUP BY p.id, p."ProductName"
                ORDER BY SUM(oi.quantity) DESC
                LIMIT 10
            """)
            product_rows = cursor.fetchall()
            for pr in product_rows:
                TopProduct.objects.create(
                    product_id=pr[0],
                    product_name=pr[1],
                    units_sold=pr[2],
                    revenue=float(pr[3] or 0)
                )
    except Exception as e:
        print(f"Error syncing top products: {e}")

    print("Sync complete.")

if __name__ == '__main__':
    sync_reports()
