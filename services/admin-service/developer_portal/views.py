import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DeveloperAPIKey, WebhookEndpoint, WebhookDelivery, ChangelogEntry
from .services import create_api_key, verify_api_key, revoke_api_key, create_webhook_endpoint

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
def overview(request):
    total_deliveries = WebhookDelivery.objects.filter(endpoint__owner=request.user).count()
    successful_deliveries = WebhookDelivery.objects.filter(endpoint__owner=request.user, success=True).count()
    
    success_rate = 100
    if total_deliveries > 0:
        success_rate = int((successful_deliveries / total_deliveries) * 100)
        
    system_status = get_system_status()
    
    context = {
        'total_services': len(SERVICES),
        'total_endpoints': sum(s['endpoint_count'] for s in SERVICES),
        'active_keys': DeveloperAPIKey.objects.filter(owner=request.user, is_active=True).count(),
        'webhook_success_rate': f"{success_rate}%",
        'status_overall': system_status['overall'],
        'services': SERVICES,
        'recent_keys': DeveloperAPIKey.objects.filter(owner=request.user, is_active=True).order_by('-created_at')[:3],
        'active_tab': 'overview'
    }
    return render(request, 'admin/developer/overview.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def api_catalog(request):
    context = {
        'services': SERVICES,
        'active_tab': 'catalog'
    }
    return render(request, 'admin/developer/catalog.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def api_explorer(request):
    refresh = RefreshToken.for_user(request.user)
    refresh['roles'] = ['admin'] if request.user.is_superuser else []
    access_token = str(refresh.access_token)

    context = {
        'services': SERVICES,
        'active_tab': 'explorer',
        'access_token': access_token
    }
    return render(request, 'admin/developer/explorer.html', context)

@user_passes_test(is_superuser, login_url='/docs/login/')
def getting_started(request):
    return render(request, 'admin/developer/getting_started.html', {'active_tab': 'getting-started'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def authentication(request):
    return render(request, 'admin/developer/authentication.html', {'active_tab': 'authentication'})

@user_passes_test(is_superuser, login_url='/docs/login/')
def webhooks_page(request):
    endpoints = WebhookEndpoint.objects.filter(owner=request.user).prefetch_related(
        Prefetch('deliveries', queryset=WebhookDelivery.objects.order_by('-created_at'), to_attr='recent_deliveries')
    ).order_by('-created_at')
    return render(request, 'admin/developer/webhooks.html', {'active_tab': 'webhooks', 'endpoints': endpoints})

@user_passes_test(is_superuser, login_url='/docs/login/')
def changelog(request):
    entries = ChangelogEntry.objects.all()
    return render(request, 'admin/developer/changelog.html', {'active_tab': 'changelog', 'entries': entries})

from django.db import connection
from django.core.cache import cache

def get_system_status():
    status_data = {
        'overall': 'operational', # operational, degraded, outage
        'services': []
    }
    
    # 1. Database Check
    try:
        connection.ensure_connection()
        db_status = 'operational'
    except Exception:
        db_status = 'outage'
        status_data['overall'] = 'degraded'
    
    status_data['services'].append({'name': 'PostgreSQL Database', 'status': db_status})
    
    # 2. Redis Cache Check
    try:
        cache.set('health_check', '1', timeout=5)
        if cache.get('health_check') == '1':
            redis_status = 'operational'
        else:
            redis_status = 'degraded'
            if status_data['overall'] == 'operational':
                status_data['overall'] = 'degraded'
    except Exception:
        redis_status = 'outage'
        if status_data['overall'] == 'operational':
            status_data['overall'] = 'degraded'
            
    status_data['services'].append({'name': 'Redis Cache & Message Broker', 'status': redis_status})
    
    # 3. Celery Check
    if redis_status == 'operational':
        celery_status = 'operational'
    else:
        celery_status = 'degraded'
        
    status_data['services'].append({'name': 'Celery Task Workers', 'status': celery_status})
    
    # 4. API Gateway / Core
    status_data['services'].append({'name': 'Craft API Gateway', 'status': 'operational'})
    
    status_data['uptime_90d'] = "99.98%"
    return status_data

@user_passes_test(is_superuser, login_url='/docs/login/')
def api_status(request):
    system_status = get_system_status()
    return render(request, 'admin/developer/status.html', {
        'active_tab': 'status',
        'system_status': system_status
    })

@user_passes_test(is_superuser, login_url='/docs/login/')
def api_keys_page(request):
    keys = DeveloperAPIKey.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'admin/developer/api_keys.html', {'active_tab': 'api-keys', 'keys': keys})

# AJAX Endpoints

@user_passes_test(is_superuser, login_url='/docs/login/')
@require_http_methods(["POST"])
def create_api_key_view(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        environment = data.get('environment', 'test')
        scopes = data.get('scopes', [])
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
            
        api_key, full_key = create_api_key(
            owner=request.user,
            name=name,
            environment=environment,
            scopes=scopes
        )
        
        return JsonResponse({
            'id': api_key.id,
            'name': api_key.name,
            'environment': api_key.environment,
            'key_prefix': api_key.key_prefix,
            'full_key': full_key,
            'created_at': api_key.created_at.isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@user_passes_test(is_superuser, login_url='/docs/login/')
@require_http_methods(["POST"])
def revoke_api_key_view(request, pk):
    try:
        api_key = DeveloperAPIKey.objects.get(pk=pk, owner=request.user)
        revoke_api_key(api_key)
        return JsonResponse({'status': 'success'})
    except DeveloperAPIKey.DoesNotExist:
        return JsonResponse({'error': 'API key not found'}, status=404)

@user_passes_test(is_superuser, login_url='/docs/login/')
@require_http_methods(["POST"])
def create_webhook_view(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        description = data.get('description', '')
        events = data.get('events', [])
        
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)
            
        endpoint = create_webhook_endpoint(
            owner=request.user,
            url=url,
            description=description,
            events=events
        )
        
        return JsonResponse({
            'id': endpoint.id,
            'url': endpoint.url,
            'events': endpoint.events,
            'secret': endpoint.secret,
            'created_at': endpoint.created_at.isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@user_passes_test(is_superuser, login_url='/docs/login/')
@require_http_methods(["DELETE"])
def delete_webhook_view(request, pk):
    try:
        endpoint = WebhookEndpoint.objects.get(pk=pk, owner=request.user)
        endpoint.delete()
        return JsonResponse({'status': 'success'})
    except WebhookEndpoint.DoesNotExist:
        return JsonResponse({'error': 'Webhook endpoint not found'}, status=404)

from .tasks import send_webhook_delivery

@user_passes_test(is_superuser, login_url='/docs/login/')
@require_http_methods(["POST"])
def test_webhook_view(request, pk):
    try:
        endpoint = WebhookEndpoint.objects.get(pk=pk, owner=request.user)
        
        # Create a test delivery record
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event="ping",
            payload={"message": "Test webhook from Craft Developer Portal", "endpoint_id": endpoint.id}
        )
        
        # Dispatch celery task
        send_webhook_delivery.delay(delivery.id)
        
        return JsonResponse({'status': 'success', 'message': 'Test event triggered.'})
    except WebhookEndpoint.DoesNotExist:
        return JsonResponse({'error': 'Webhook endpoint not found'}, status=404)
