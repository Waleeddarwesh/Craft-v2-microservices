from django import template
from django.db import connection
from django.conf import settings
import redis

register = template.Library()

@register.inclusion_tag('admin/health_widget.html')
def render_health_widget():
    health = {"database": "down", "redis": "down"}
    try:
        connection.cursor()
        health["database"] = "up"
    except Exception:
        pass
        
    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        r.ping()
        health["redis"] = "up"
    except Exception:
        pass
        
    return {"health": health}
