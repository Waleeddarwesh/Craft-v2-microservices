from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def admin_profile_settings(request):
    if request.method == "POST":
        user = request.user
        updated = False

        # Handle Profile Picture Upload


        # Handle Password Change
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password and confirm_password:
            if password == confirm_password:
                if len(password) >= 8:
                    user.set_password(password)
                    user.must_change_password = False
                    update_session_auth_hash(request, user) # Keep user logged in
                    updated = True
                    messages.success(request, "Password updated successfully!")
                else:
                    messages.error(request, "Password must be at least 8 characters long.")
            else:
                messages.error(request, "Passwords do not match.")

        if updated:
            user.save()
            if not messages.get_messages(request): # If no specific password success message
                messages.success(request, "Profile updated successfully!")
            return redirect('admin_profile_settings')

    return render(request, 'admin/profile_settings.html', {
        'title': 'Account Settings',
        'is_popup': False,
        'has_permission': True,
    })
