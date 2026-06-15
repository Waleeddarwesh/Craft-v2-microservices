from django.urls import path
from orders.admin_views import AdminOrdersView, AdminReturnsView, AdminReturnActionView, AdminCouponsView

urlpatterns = [
    path('orders/', AdminOrdersView.as_view()),
    path('returns/', AdminReturnsView.as_view()),
    path('returns/<uuid:pk>/action/', AdminReturnActionView.as_view()),
    path('coupons/', AdminCouponsView.as_view()),
]
