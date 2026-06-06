from django.urls import path
from . import views

urlpatterns = [
    # --- Identity & Config ---
    path('me/', views.DashboardIdentityView.as_view(), name='admin-identity'),

    # --- KPI & Chart Data ---
    path('search/', views.AdminGlobalSearchView.as_view(), name='admin-global-search'),
    path('stats/', views.AdminStatsView.as_view(), name='admin-stats'),
    path('charts/', views.AdminChartsView.as_view(), name='admin-charts'),
    path('reports/', views.AdminSystemReportsView.as_view(), name='admin-reports'),
    path('health/', views.AdminSystemHealthView.as_view(), name='admin-health'),
    path('top-products/', views.AdminTopProductsView.as_view(), name='admin-top-products'),
    path('recent-activity/', views.AdminRecentActivityView.as_view(), name='admin-recent-activity'),
    path('audit-logs/', views.AdminAuditLogsView.as_view(), name='admin-audit-logs'),
    
    # --- Performance Endpoints ---
    path('performance/suppliers/', views.AdminSupplierPerformanceView.as_view(), name='admin-supplier-performance'),
    path('performance/delivery/', views.AdminDeliveryPerformanceView.as_view(), name='admin-delivery-performance'),
    path('finance/reconciliation/', views.AdminFinancialReconciliationView.as_view(), name='admin-financial-reconciliation'),
    path('fraud-alerts/', views.AdminFraudAlertsView.as_view(), name='admin-fraud-alerts'),
    path('fraud-alerts/<int:pk>/action/', views.AdminFraudAlertActionView.as_view(), name='admin-fraud-alert-action'),
    path('moderation/products/', views.AdminProductModerationView.as_view(), name='admin-moderation-products'),
    path('moderation/products/<int:pk>/action/', views.AdminProductModerationActionView.as_view(), name='admin-moderation-products-action'),

    # --- Entity List Endpoints (admin sees ALL records) ---
    path('orders/', views.AdminOrdersView.as_view(), name='admin-orders'),
    path('orders/<uuid:pk>/status/', views.AdminOrderStatusView.as_view(), name='admin-order-status'),
    path('products/', views.AdminProductsView.as_view(), name='admin-products'),
    path('returns/', views.AdminReturnsView.as_view(), name='admin-returns-list'),
    path('courses/', views.AdminCoursesView.as_view(), name='admin-courses'),
    path('reviews/', views.AdminReviewsView.as_view(), name='admin-reviews'),
    path('coupons/', views.AdminCouponsView.as_view(), name='admin-coupons'),
    path('transactions/', views.AdminTransactionsView.as_view(), name='admin-transactions'),
    path('withdrawals/', views.AdminWithdrawalsListView.as_view(), name='admin-withdrawals-list'),
    path('payments/', views.AdminPaymentsView.as_view(), name='admin-payments'),
    path('notifications/', views.AdminNotificationsView.as_view(), name='admin-notifications'),
    path('support-tickets/', views.AdminSupportTicketsView.as_view(), name='admin-support-tickets'),
    path('support-tickets/<int:pk>/', views.AdminSupportTicketDetailView.as_view(), name='admin-support-ticket-detail'),
    path('disputes/', views.AdminDisputesView.as_view(), name='admin-disputes'),
    path('disputes/<int:pk>/', views.AdminDisputeDetailView.as_view(), name='admin-dispute-detail'),

    # --- User Management ---
    path('users/', views.AdminUsersView.as_view(), name='admin-users'),
    path('users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:pk>/toggle/', views.AdminUserToggleView.as_view(), name='admin-user-toggle'),
    path('users/supplier/<int:pk>/', views.AdminSupplierApprovalView.as_view(), name='admin-supplier-approval'),
    path('users/delivery/<int:pk>/', views.AdminDeliveryApprovalView.as_view(), name='admin-delivery-approval'),
    path('notifications/send/', views.AdminSendNotificationView.as_view(), name='admin-send-notification'),

    # --- Admin Actions ---
    path('returns/<uuid:pk>/action/', views.AdminReturnActionView.as_view(), name='admin-return-action'),
    path('withdrawals/<uuid:pk>/action/', views.AdminWithdrawalActionView.as_view(), name='admin-withdrawal-action'),
    path('reviews/<int:pk>/action/', views.AdminReviewModerationView.as_view(), name='admin-review-action'),
]
