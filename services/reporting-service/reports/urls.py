from django.urls import path
from .views import EarningReportView, SupplierAnalyticsView

urlpatterns = [
    path('earnings/', EarningReportView.as_view(), name='earning-report'),
    path('supplier-analytics/', SupplierAnalyticsView.as_view(), name='supplier-analytics'),
]