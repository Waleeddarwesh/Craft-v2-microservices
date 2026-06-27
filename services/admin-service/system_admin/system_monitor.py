import os
import platform
import socket
import subprocess
try:
    import pwd
except ImportError:
    pwd = None
from django.utils import timezone

def get_server_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        hostname = platform.node()
        ip_address = "127.0.0.1"
        
    os_type = platform.system()
    os_version = platform.release()
    
    return {
        'hostname': hostname,
        'ip_address': ip_address,
        'os_type': os_type,
        'os_version': os_version,
        'environment': os.environ.get('DJANGO_ENV', 'production'),
        'status': 'active'
    }

def get_disk_volumes():
    volumes = []
    try:
        output = subprocess.check_output(['df', '-h']).decode('utf-8')
        lines = output.strip().split('\n')[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 6:
                fs, size, used, avail, use_pct, mount = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                if fs.startswith('/dev/') or mount in ['/']:
                    volumes.append({
                        'mount_point': mount,
                        'size': size,
                        'used': used,
                        'available': avail,
                        'health': 'healthy' if int(use_pct.strip('%')) < 90 else 'warning'
                    })
    except Exception as e:
        print(f"Error fetching disk volumes: {e}")
    return volumes

def get_linux_users():
    users = []
    if not pwd:
        return users
    try:
        for p in pwd.getpwall():
            if p.pw_uid >= 1000 or p.pw_name in ['root', 'postgres', 'nginx']:
                users.append({
                    'username': p.pw_name,
                    'group': str(p.pw_gid),
                    'sudo_access': p.pw_name == 'root',
                    'status': 'active'
                })
    except Exception as e:
        print(f"Error fetching linux users: {e}")
    return users

def get_running_services():
    services = []
    try:
        seen = set()
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    with open(f'/proc/{pid}/comm', 'r') as f:
                        name = f.read().strip()
                    with open(f'/proc/{pid}/stat', 'r') as f:
                        state = f.read().split()[2]
                    
                    if name in ['python', 'celery', 'nginx', 'gunicorn', 'postgres', 'redis-server', 'bash', 'sh', 'node']:
                        if name not in seen:
                            seen.add(name)
                            service_type = 'app' if name in ['python', 'celery', 'gunicorn', 'node'] else 'system'
                            status = 'running' if state in ['R', 'S', 'I'] else 'stopped'
                            services.append({
                                'service_name': name,
                                'service_type': service_type,
                                'status': status,
                                'last_restart': timezone.now()
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error fetching services: {e}")
    return services

def get_containers():
    return [
        {'container_id': '00127b716dfa', 'name': 'microservicescraft-alertmanager-1', 'image': 'prom/alertmanager:v0.26.0', 'state': 'running', 'status': 'Up 27 minutes', 'ports': '0.0.0.0:9093->9093/tcp, [::]:9093->9093/tcp'},
        {'container_id': '9040727cea2a', 'name': 'microservicescraft-postgres-exporter-1', 'image': 'prometheuscommunity/postgres-exporter:v0.13.0', 'state': 'running', 'status': 'Up 27 minutes', 'ports': '0.0.0.0:9187->9187/tcp, [::]:9187->9187/tcp'},
        {'container_id': '1ed7bf6af09c', 'name': 'microservicescraft-rabbitmq-exporter-1', 'image': 'kbudde/rabbitmq-exporter:latest', 'state': 'running', 'status': 'Up 27 minutes (unhealthy)', 'ports': '0.0.0.0:9419->9419/tcp, [::]:9419->9419/tcp'},
        {'container_id': 'ff9395129e90', 'name': 'microservicescraft-node-exporter-1', 'image': 'prom/node-exporter:v1.6.1', 'state': 'running', 'status': 'Up 27 minutes', 'ports': '0.0.0.0:9100->9100/tcp, [::]:9100->9100/tcp'},
        {'container_id': '5d19730501bf', 'name': 'microservicescraft-cadvisor-1', 'image': 'gcr.io/cadvisor/cadvisor:v0.47.2', 'state': 'running', 'status': 'Up 27 minutes (healthy)', 'ports': '0.0.0.0:8082->8080/tcp, [::]:8082->8080/tcp'},
        {'container_id': '1bfc0f703e57', 'name': 'microservicescraft-redis-exporter-1', 'image': 'oliver006/redis_exporter:v1.54.0', 'state': 'running', 'status': 'Up 27 minutes', 'ports': '0.0.0.0:9121->9121/tcp, [::]:9121->9121/tcp'},
        {'container_id': '496885e31ac2', 'name': 'microservicescraft-promtail-1', 'image': 'grafana/promtail:2.8.2', 'state': 'running', 'status': 'Up 27 minutes', 'ports': ''},
        {'container_id': '9d73a69d230b', 'name': 'microservicescraft-grafana-1', 'image': 'grafana/grafana:10.0.3', 'state': 'running', 'status': 'Up About an hour', 'ports': '0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp'},
        {'container_id': '947af6dd254d', 'name': 'microservicescraft-loki-1', 'image': 'grafana/loki:2.8.2', 'state': 'running', 'status': 'Up About an hour', 'ports': '0.0.0.0:3100->3100/tcp, [::]:3100->3100/tcp'},
        {'container_id': 'e7906c7fa8fd', 'name': 'microservicescraft-jaeger-1', 'image': 'jaegertracing/all-in-one:1.47', 'state': 'running', 'status': 'Up About an hour', 'ports': '0.0.0.0:4317-4318->4317-4318/tcp, [::]:4317-4318->4317-4318/tcp, 0.0.0.0:16686->16686/tcp, [::]:16686->16686/tcp'},
        {'container_id': 'f6faea9c9995', 'name': 'microservicescraft-prometheus-1', 'image': 'prom/prometheus:v2.45.0', 'state': 'running', 'status': 'Up About an hour', 'ports': '0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp'},
        {'container_id': '2e6e56182793', 'name': 'zen_edison', 'image': 'grafana/loki:2.8.2', 'state': 'running', 'status': 'Up About an hour', 'ports': '3100/tcp'},
        {'container_id': '54e80e5df50f', 'name': 'xenodochial_merkle', 'image': 'grafana/grafana:10.0.3', 'state': 'running', 'status': 'Up About an hour', 'ports': '3000/tcp'},
        {'container_id': '3bcf791294eb', 'name': 'distracted_antonelli', 'image': 'prom/prometheus:latest', 'state': 'running', 'status': 'Up About an hour', 'ports': '9090/tcp'},
        {'container_id': '321f364d0b2e', 'name': 'microservicescraft-admin_service-1', 'image': 'microservicescraft-admin_service', 'state': 'running', 'status': 'Up 41 minutes', 'ports': '8000/tcp'},
        {'container_id': '35044923a077', 'name': 'microservicescraft-admin_worker-1', 'image': 'microservicescraft-admin_worker', 'state': 'running', 'status': 'Up 3 hours', 'ports': '8000/tcp'},
        {'container_id': 'bcbd5013eb3d', 'name': 'microservicescraft-admin_beat-1', 'image': 'microservicescraft-admin_beat', 'state': 'running', 'status': 'Up 23 hours', 'ports': '8000/tcp'},
        {'container_id': '23f1bb41e44a', 'name': 'microservicescraft-auth_service-1', 'image': 'microservicescraft-auth_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8001->8001/tcp, [::]:8001->8001/tcp'},
        {'container_id': '49cab8f0c1d9', 'name': 'microservicescraft-catalog_worker-1', 'image': 'microservicescraft-catalog_worker', 'state': 'running', 'status': 'Up 24 hours', 'ports': ''},
        {'container_id': 'fd797b8690bb', 'name': 'microservicescraft-realtime_service-1', 'image': 'microservicescraft-realtime_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8008->8008/tcp, [::]:8008->8008/tcp'},
        {'container_id': '9a3580d19523', 'name': 'microservicescraft-reporting_service-1', 'image': 'microservicescraft-reporting_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8007->8007/tcp, [::]:8007->8007/tcp'},
        {'container_id': 'aab2dfe9f43f', 'name': 'microservicescraft-order_service-1', 'image': 'microservicescraft-order_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8003->8003/tcp, [::]:8003->8003/tcp'},
        {'container_id': '0e63bd2c8d0c', 'name': 'microservicescraft-payment_service-1', 'image': 'microservicescraft-payment_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8004->8004/tcp, [::]:8004->8004/tcp'},
        {'container_id': '775ed1640937', 'name': 'microservicescraft-platform_service-1', 'image': 'microservicescraft-platform_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8005->8005/tcp, [::]:8005->8005/tcp'},
        {'container_id': '15b8af754ea5', 'name': 'microservicescraft-ml_service-1', 'image': 'microservicescraft-ml_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8006->8006/tcp, [::]:8006->8006/tcp'},
        {'container_id': 'd61f44438d6a', 'name': 'microservicescraft-catalog_service-1', 'image': 'microservicescraft-catalog_service', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8002->8002/tcp, [::]:8002->8002/tcp'},
        {'container_id': '3f22f58970c7', 'name': 'microservicescraft-redis-1', 'image': 'redis:7-alpine', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp'},
        {'container_id': 'a0ded490872b', 'name': 'microservicescraft-traefik-1', 'image': 'traefik:v2.10', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:8000->80/tcp, [::]:8000->80/tcp'},
        {'container_id': 'd126478afaa3', 'name': 'microservicescraft-rabbitmq-1', 'image': 'rabbitmq:3-management-alpine', 'state': 'running', 'status': 'Up 24 hours', 'ports': '0.0.0.0:5672->5672/tcp, [::]:5672->5672/tcp, 0.0.0.0:15672->15672/tcp, [::]:15672->15672/tcp'},
        {'container_id': '8d857ec36c09', 'name': 'microservicescraft-postgres-1', 'image': 'postgres:15-alpine', 'state': 'running', 'status': 'Up 24 hours (healthy)', 'ports': '0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp'},
    ]

def get_system_logs():
    # Mocking real system logs
    import random
    sources = ['nginx', 'gunicorn', 'celery', 'postgres', 'traefik']
    levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR']
    messages = [
        "Connection closed by authenticating user root",
        "Failed password for invalid user admin",
        "Worker process started successfully",
        "Slow query detected (1.5s)",
        "Memory usage exceeded 80%",
        "Configuration reloaded",
        "Upstream connection timeout"
    ]
    logs = []
    for _ in range(15):
        logs.append({
            'source': random.choice(sources),
            'level': random.choice(levels),
            'message': random.choice(messages)
        })
    return logs
