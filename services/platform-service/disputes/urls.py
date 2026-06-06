from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DisputeViewSet

router = DefaultRouter()
router.register(r'disputes', DisputeViewSet, basename='disputes')

urlpatterns = [
    path('', include(router.urls)),
]
