from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from developer_portal.models import APIService

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_overview(request):
    services = APIService.objects.all()
    context = {
        'total_services': services.count(),
        'total_endpoints': sum(s.endpoint_count for s in services),
        'active_keys': 12, # Still mock for now as keys wasn't requested
        'services': services,
        'active_tab': 'overview'
    }
    return render(request, 'admin/developer/overview.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_catalog(request):
    services = APIService.objects.all()
    context = {
        'services': services,
        'active_tab': 'catalog'
    }
    return render(request, 'admin/developer/catalog.html', context)

from rest_framework_simplejwt.tokens import RefreshToken

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_explorer(request):
    refresh = RefreshToken.for_user(request.user)
    refresh['roles'] = ['admin'] if request.user.is_superuser else []
    access_token = str(refresh.access_token)

    services = APIService.objects.all()
    # This renders the embedded Swagger UI
    context = {
        'services': services,
        'active_tab': 'explorer',
        'access_token': access_token
    }
    return render(request, 'admin/developer/explorer.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_getting_started(request):
    context = {
        'active_tab': 'getting-started'
    }
    return render(request, 'admin/developer/getting_started.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_authentication(request):
    return render(request, 'admin/developer/authentication.html', {'active_tab': 'authentication'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_webhooks(request):
    return render(request, 'admin/developer/webhooks.html', {'active_tab': 'webhooks'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_changelog(request):
    return render(request, 'admin/developer/changelog.html', {'active_tab': 'changelog'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_status(request):
    return render(request, 'admin/developer/status.html', {'active_tab': 'status'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_api_keys(request):
    return render(request, 'admin/developer/api_keys.html', {'active_tab': 'api-keys'})
