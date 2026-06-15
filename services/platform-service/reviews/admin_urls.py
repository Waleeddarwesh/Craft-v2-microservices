from django.urls import path
from .admin_views import (
    AdminReviewsView, AdminReviewActionView,
    AdminDisputesView, AdminDisputeDetailView,
    AdminSupportTicketsView, AdminSupportTicketDetailView,
    AdminFraudAlertsView, AdminFraudAlertActionView
)

urlpatterns = [
    path('reviews/', AdminReviewsView.as_view()),
    path('reviews/<int:pk>/action/', AdminReviewActionView.as_view()),
    
    path('disputes/', AdminDisputesView.as_view()),
    path('disputes/<int:pk>/', AdminDisputeDetailView.as_view()),
    path('disputes/<int:pk>/action/', AdminDisputeDetailView.as_view()), # For patch
    
    path('support-tickets/', AdminSupportTicketsView.as_view()),
    path('support-tickets/<int:pk>/', AdminSupportTicketDetailView.as_view()),
    path('support-tickets/<int:pk>/action/', AdminSupportTicketDetailView.as_view()), # For post
    
    path('fraud-alerts/', AdminFraudAlertsView.as_view()),
    path('fraud-alerts/<int:pk>/action/', AdminFraudAlertActionView.as_view()),
    
]
