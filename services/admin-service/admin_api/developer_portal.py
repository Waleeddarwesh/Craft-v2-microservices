from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# Mock data for Phase 1
SERVICES = [
    {
        "name": "Catalog & Video Service",
        "slug": "catalog-video",
        "version": "v2.0",
        "status": "healthy",
        "description": "Products, courses, videos, and catalog management APIs.",
        "schema_url": "/product/api/schema/?v=2",
        "endpoint_count": 42
    },
    {
        "name": "Orders Service",
        "slug": "orders",
        "version": "v2.0",
        "status": "healthy",
        "description": "Manage customer orders, shopping carts, and returns.",
        "schema_url": "/orders/api/schema/?v=2",
        "endpoint_count": 28
    },
    {
        "name": "Payments Service",
        "slug": "payments",
        "version": "v2.0",
        "status": "healthy",
        "description": "Process payments, refunds, and financial transactions.",
        "schema_url": "/payment/api/schema/?v=2",
        "endpoint_count": 15
    },
    {
        "name": "Platform Service",
        "slug": "platform",
        "version": "v2.0",
        "status": "healthy",
        "description": "Platform-wide features like reviews, disputes, and settings.",
        "schema_url": "/review/api/schema/?v=2",
        "endpoint_count": 31
    },
    {
        "name": "Reporting Service",
        "slug": "reporting",
        "version": "v2.0",
        "status": "healthy",
        "description": "Analytics, charts, and audit logs.",
        "schema_url": "/reports/api/schema/?v=2",
        "endpoint_count": 12
    },
    {
        "name": "Auth Service",
        "slug": "auth",
        "version": "v2.0",
        "status": "healthy",
        "description": "User authentication, JWT generation, and OAuth integration.",
        "schema_url": "/accounts/api/schema/?v=2",
        "endpoint_count": 18
    },
    {
        "name": "Admin API",
        "slug": "admin",
        "version": "v2.0",
        "status": "healthy",
        "description": "Central management API for the Craft Dashboard.",
        "schema_url": "/admin-schema.json?format=openapi&v=2",
        "endpoint_count": 56
    },
    {
        "name": "ML Recommendations",
        "slug": "ml",
        "version": "v1.0",
        "status": "healthy",
        "description": "AI-driven product and course recommendations (FastAPI).",
        "schema_url": "/recommendations/openapi.json",
        "endpoint_count": 5
    }
]

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_overview(request):
    context = {
        'total_services': len(SERVICES),
        'total_endpoints': sum(s['endpoint_count'] for s in SERVICES),
        'active_keys': 12, # mock
        'services': SERVICES,
        'active_tab': 'overview'
    }
    return render(request, 'admin/developer/overview.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_catalog(request):
    context = {
        'services': SERVICES,
        'active_tab': 'catalog'
    }
    return render(request, 'admin/developer/catalog.html', context)

from rest_framework_simplejwt.tokens import RefreshToken

@user_passes_test(is_superuser, login_url='/docs/login/')
def developer_explorer(request):
    refresh = RefreshToken.for_user(request.user)
    refresh['roles'] = ['admin'] if request.user.is_superuser else []
    access_token = str(refresh.access_token)

    # This renders the embedded Swagger UI
    context = {
        'services': SERVICES,
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
