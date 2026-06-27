from django.urls import path
from . import internal_views

urlpatterns = [
    path('users/<int:user_id>/', internal_views.InternalUserDetailView.as_view()),
    path('users/bulk-lookup/', internal_views.InternalUserBulkLookupView.as_view()),
    path('users/<int:user_id>/fcm-token/', internal_views.InternalUserFCMTokenView.as_view()),
    path('stats/user-counts/', internal_views.InternalUserStatsView.as_view()),
]
