from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from ingestion.models import DataSource
import uuid

class KPI(models.Model):
    """Definición de un KPI (Key Performance Indicator)"""
    METRIC_TYPES = [
        ('sum', 'Suma'),
        ('avg', 'Promedio'),
        ('count', 'Conteo'),
        ('max', 'Máximo'),
        ('min', 'Mínimo'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del KPI")
    description = models.TextField(blank=True, verbose_name="Descripción")
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, verbose_name="Fuente de datos")
    table_name = models.CharField(max_length=100, verbose_name="Tabla específica", default='default_table', help_text="Tabla dentro del esquema de la fuente de datos")
    metric_type = models.CharField(max_length=10, choices=METRIC_TYPES, verbose_name="Tipo de métrica")
    column_name = models.CharField(max_length=100, verbose_name="Columna a medir")
    filter_conditions = models.JSONField(default=dict, blank=True, verbose_name="Condiciones de filtro")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_metric_type_display()})"
    
    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"

class AlertRule(models.Model):
    """Reglas de alerta para los KPIs"""
    COMPARISON_OPERATORS = [
        ('gt', 'Mayor que (>)'),
        ('gte', 'Mayor o igual que (>=)'),
        ('lt', 'Menor que (<)'),
        ('lte', 'Menor o igual que (<=)'),
        ('eq', 'Igual a (=)'),
        ('ne', 'Diferente de (!=)'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la regla")
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='alert_rules')
    comparison_operator = models.CharField(max_length=10, choices=COMPARISON_OPERATORS)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor umbral")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Configuración de notificaciones
    send_email = models.BooleanField(default=True, verbose_name="Enviar por email")
    email_recipients = models.JSONField(default=list, blank=True, verbose_name="Destinatarios de email")
    send_in_app = models.BooleanField(default=True, verbose_name="Notificación en la app")
    
    def __str__(self):
        return f"{self.name} - {self.kpi.name}"
    
    class Meta:
        verbose_name = "Regla de Alerta"
        verbose_name_plural = "Reglas de Alerta"

class Alert(models.Model):
    """Registro de alertas disparadas"""
    STATUS_CHOICES = [
        ('new', 'Nueva'),
        ('acknowledged', 'Reconocida'),
        ('resolved', 'Resuelta'),
        ('dismissed', 'Descartada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Valores que dispararon la alerta
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Metadatos adicionales
    message = models.TextField(blank=True)
    context_data = models.JSONField(default=dict, blank=True)
    
    # Control de estado
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Alerta: {self.alert_rule.name} - {self.get_status_display()}"

class NotificationLog(models.Model):
    """Log de notificaciones enviadas"""
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('in_app', 'En la aplicación'),
        ('sms', 'SMS'),  # para futuras implementaciones
    ]
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.CharField(max_length=255, verbose_name="Destinatario")
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Log de Notificación"
        verbose_name_plural = "Logs de Notificaciones"
