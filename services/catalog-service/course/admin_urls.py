from django.urls import path
from .admin_views import AdminCoursesView

urlpatterns = [
    path('courses/', AdminCoursesView.as_view()),
]
