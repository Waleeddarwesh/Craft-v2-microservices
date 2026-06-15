from django.urls import path
from .admin_views import AdminPaymentsView, AdminTransactionsView, AdminWithdrawalsView, AdminWithdrawalActionView

urlpatterns = [
    path('payments/', AdminPaymentsView.as_view()),
    path('transactions/', AdminTransactionsView.as_view()),
    path('withdrawals/', AdminWithdrawalsView.as_view()),
    path('withdrawals/<uuid:pk>/action/', AdminWithdrawalActionView.as_view()),
]
