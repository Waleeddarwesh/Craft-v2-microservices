from rest_framework import serializers
from .models import (
    Server, AuditLog, Service, LinuxUser, CronJob, Incident, OperationalScript,
    DiskVolume, LogicalVolume, BackupJob, FirewallRule, SecurityAlert, SELinuxContext,
    Container, SystemLog
)

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = Service
        fields = '__all__'

class LinuxUserSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = LinuxUser
        fields = '__all__'

class CronJobSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = CronJob
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True, default=None)
    class Meta:
        model = Incident
        fields = '__all__'

class OperationalScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalScript
        fields = '__all__'

class DiskVolumeSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = DiskVolume
        fields = '__all__'

class LogicalVolumeSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = LogicalVolume
        fields = '__all__'

class BackupJobSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = BackupJob
        fields = '__all__'

class FirewallRuleSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = FirewallRule
        fields = '__all__'

class SecurityAlertSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = SecurityAlert
        fields = '__all__'

class SELinuxContextSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    class Meta:
        model = SELinuxContext
        fields = '__all__'

class ContainerSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True, default=None)
    class Meta:
        model = Container
        fields = '__all__'

class SystemLogSerializer(serializers.ModelSerializer):
    server_hostname = serializers.CharField(source='server.hostname', read_only=True, default=None)
    class Meta:
        model = SystemLog
        fields = '__all__'
