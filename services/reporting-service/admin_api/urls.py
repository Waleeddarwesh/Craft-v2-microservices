from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.DashboardOverviewView.as_view(), name='admin-stats'),
    path('health/', views.SystemHealthView.as_view(), name='admin-health'),
    path('top-products/', views.TopProductsView.as_view(), name='admin-top-products'),
    path('revenue/', views.RevenueReportView.as_view(), name='admin-revenue'),
    path('supplier-analytics/', views.SupplierAnalyticsView.as_view(), name='admin-supplier-analytics'),
    path('charts/', views.AdminChartsView.as_view()),
    path('recent-activity/', views.AdminRecentActivityView.as_view()),
    path('audit-logs/', views.AdminAuditLogsView.as_view()),
    path('reports/', views.AdminReportsView.as_view()),
    path('performance/suppliers/', views.AdminSupplierPerformanceView.as_view()),
    path('performance/delivery/', views.AdminDeliveryPerformanceView.as_view()),
    path('finance/reconciliation/', views.AdminReconciliationView.as_view()),
]

