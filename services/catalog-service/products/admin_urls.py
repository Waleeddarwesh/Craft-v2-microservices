from django.urls import path
from .admin_views import AdminProductsView, AdminProductModerationView, AdminProductModerationActionView

urlpatterns = [
    path('products/', AdminProductsView.as_view()),
    path('moderation/products/', AdminProductModerationView.as_view()),
    path('moderation/products/<int:pk>/action/', AdminProductModerationActionView.as_view()),
]
