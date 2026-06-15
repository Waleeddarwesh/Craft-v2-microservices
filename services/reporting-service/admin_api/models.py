from django.db import models

class AnalyticsAggregate(models.Model):
    metric_name = models.CharField(max_length=255)
    dimension = models.CharField(max_length=255, null=True, blank=True)
    dimension_id = models.CharField(max_length=255, null=True, blank=True)
    dimension_name = models.CharField(max_length=255, null=True, blank=True)
    value = models.FloatField()
    period = models.CharField(max_length=50) # daily, monthly

    def __str__(self):
        return f"{self.metric_name} - {self.dimension}"

class DailyRevenueSummary(models.Model):
    date = models.DateField()
    gross_revenue = models.FloatField()
    order_count = models.IntegerField()
    refund_amount = models.FloatField()
    net_revenue = models.FloatField()

    def __str__(self):
        return str(self.date)

class TopProduct(models.Model):
    product_id = models.BigIntegerField()
    product_name = models.CharField(max_length=255)
    units_sold = models.IntegerField()
    revenue = models.FloatField()

    def __str__(self):
        return self.product_name
