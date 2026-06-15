from django.urls import path
from .admin_views import AdminUsersView, AdminUserDetailView, AdminMeView, AdminSupplierActionView, AdminDeliveryActionView

urlpatterns = [
    path('users/', AdminUsersView.as_view()),
    path('users/<int:pk>/', AdminUserDetailView.as_view()),
    path('users/supplier/<int:pk>/', AdminSupplierActionView.as_view()),
    path('users/delivery/<int:pk>/', AdminDeliveryActionView.as_view()),
    path('me/', AdminMeView.as_view()),
]
