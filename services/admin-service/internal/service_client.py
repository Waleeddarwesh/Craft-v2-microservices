import requests
import logging
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class ServiceClient:
    SERVICE_URLS = {
        'auth-service': 'http://auth_service:8001',
        'catalog-service': 'http://catalog_service:8002',
        'order-service': 'http://order_service:8003',
        'payment-service': 'http://payment_service:8004',
        'platform-service': 'http://platform_service:8005',
        'ml-service': 'http://ml_service:8006',
        'reporting-service': 'http://reporting_service:8007',
        'realtime-service': 'http://realtime_service:8008',
    }

    @classmethod
    def _get_base_url(cls, service_name):
        return cls.SERVICE_URLS.get(service_name)

    @classmethod
    def _prepare_headers(cls, request):
        headers = {'Content-Type': 'application/json'}
        # Forward Authorization header (JWT Token)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            headers['Authorization'] = auth_header
        return headers

    @classmethod
    def proxy_request(cls, service_name, path, request):
        """
        Proxies an incoming Django/DRF request to another microservice.
        Returns a DRF Response object.
        """
        base_url = cls._get_base_url(service_name)
        if not base_url:
            logger.error(f"Unknown service: {service_name}")
            return Response({'detail': 'Internal Service Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # Keep query parameters
        if request.META.get('QUERY_STRING'):
            url += '?' + request.META['QUERY_STRING']

        headers = cls._prepare_headers(request)
        method = request.method
        
        # Forward data if it's not a GET
        data = None
        if method not in ['GET', 'HEAD', 'OPTIONS']:
            try:
                data = request.data
            except Exception:
                data = None

        try:
            resp = requests.request(
                method=method,
                url=url,
                json=data if data else None,
                headers=headers,
                timeout=15
            )
            
            try:
                resp_data = resp.json()
            except ValueError:
                resp_data = resp.text
                
            return Response(resp_data, status=resp.status_code)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with {service_name}: {str(e)}")
            return Response({'detail': 'Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

