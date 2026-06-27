from django.db import models
from django.conf import settings

class Server(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    os_type = models.CharField(max_length=100)
    os_version = models.CharField(max_length=100)
    environment = models.CharField(max_length=50, choices=[
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ])
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ], default='active')
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    resource = models.CharField(max_length=255)
    details = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.resource} at {self.timestamp}"

class Service(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='stopped')
    last_restart = models.DateTimeField(null=True, blank=True)

class LinuxUser(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='linux_users')
    username = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    sudo_access = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='active')

class CronJob(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='cron_jobs')
    name = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100) # e.g. "0 0 * * *"
    command = models.TextField()
    user = models.CharField(max_length=50, default='root')
    status = models.CharField(max_length=20, default='active')

class Incident(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')])
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('investigating', 'Investigating'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open')
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class OperationalScript(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    script_content = models.TextField()
    interpreter = models.CharField(max_length=50, default='/bin/bash')
    created_at = models.DateTimeField(auto_now_add=True)

class DiskVolume(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='disk_volumes')
    mount_point = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    used = models.CharField(max_length=50)
    available = models.CharField(max_length=50)
    health = models.CharField(max_length=50, default='healthy')

class LogicalVolume(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='logical_volumes')
    vg_name = models.CharField(max_length=100)
    lv_name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='active')

class BackupJob(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='backup_jobs')
    name = models.CharField(max_length=255)
    backup_type = models.CharField(max_length=100) # e.g. Database, Media
    schedule = models.CharField(max_length=100) # Cron format
    status = models.CharField(max_length=50, default='active')
    last_run = models.DateTimeField(null=True, blank=True)

class FirewallRule(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='firewall_rules')
    port = models.CharField(max_length=20)
    protocol = models.CharField(max_length=20, default='tcp')
    action = models.CharField(max_length=20, choices=[('allow', 'Allow'), ('deny', 'Deny')], default='allow')
    description = models.CharField(max_length=255, blank=True)

class SecurityAlert(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='security_alerts')
    title = models.CharField(max_length=255)
    severity = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

class SELinuxContext(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='selinux_contexts')
    file_path = models.CharField(max_length=255)
    expected_context = models.CharField(max_length=255)
    current_context = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('match', 'Match'), ('mismatch', 'Mismatch')], default='match')

class Container(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='containers', null=True, blank=True)
    container_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    state = models.CharField(max_length=50) # running, exited, etc.
    status = models.CharField(max_length=100) # Up 2 hours, etc.
    ports = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.container_id[:8]})"

class SystemLog(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='system_logs', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100) # e.g. nginx, syslog, auth
    level = models.CharField(max_length=20) # INFO, WARN, ERROR, CRITICAL
    message = models.TextField()

    def __str__(self):
        return f"[{self.level}] {self.source}: {self.message[:50]}"
