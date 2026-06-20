from django.shortcuts import redirect
from django.urls import reverse
import re

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'must_change_password', False):
            # Allow access to profile settings, logout, admin logout, static files, and media
            allowed_paths = [
                reverse('admin_profile_settings'),
                reverse('docs-logout'),
                '/admin/logout/',
                '/static/',
                '/media/',
            ]
            
            # Check if current path starts with any allowed path
            if not any(request.path.startswith(path) for path in allowed_paths):
                return redirect('admin_profile_settings')

        response = self.get_response(request)
        return response
