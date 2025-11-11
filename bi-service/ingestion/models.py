# ingestion/models.py

from __future__ import annotations

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from fernet_fields import EncryptedTextField, EncryptedCharField
import pandas as pd

# Si usas execute_query que construye un engine vía services.get_engine
from .services import get_engine

User = get_user_model()


class DataSource(models.Model):
    FILE = "FILE"   # Dataset importado a tu propia BD (esquema/tabla internos)
    LIVE = "LIVE"   # Conexión en vivo a una BD externa
    TYPE_CHOICES = [
        (FILE, "Archivo importado"),
        (LIVE, "Conexión en vivo"),
    ]
    
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=TYPE_CHOICES, default=FILE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Para datasets importados o conexiones legacy (SIN ExternalConnection)
    db_host = models.CharField(max_length=255, null=True, blank=True)
    db_port = models.IntegerField(null=True, blank=True)
    db_name = models.CharField(max_length=255, null=True, blank=True)
    db_user = models.CharField(max_length=255, null=True, blank=True)
    db_password = models.CharField(max_length=255, null=True, blank=True)

    # Para datasets importados (adónde se cargó internamente)
    internal_schema = models.CharField(max_length=120, null=True, blank=True, default="")
    internal_table = models.CharField(max_length=120, null=True, blank=True, default="")

    def __str__(self) -> str:
        return f"{self.name} ({self.kind})"

    @property
    def diagramas_count(self) -> int:
        return self.diagramas.count()

    def get_db_credentials(self) -> dict:
        # 1️⃣ Si tiene una ExternalConnection asociada → usa esa
        if hasattr(self, "connection") and self.connection:
            conn = self.connection
            return {
                "host": conn.host,
                "port": conn.port,
                "database": conn.database,
                "user": conn.username,
                "password": conn.password,
                "schema": conn.extras.get("schema", "public") if conn.extras else "public",
            }

        # 2️⃣ Si el tipo es LIVE y no hay ExternalConnection → busca en settings.EXTERNAL_DBS
        if self.kind == self.LIVE:
            cfgs = getattr(settings, "EXTERNAL_DBS", {})
            cfg = cfgs.get(self.name.lower()) or cfgs.get(self.name)
            if cfg:
                return {
                    "host": cfg.get("host"),
                    "port": int(cfg.get("port", 5432)),
                    "database": cfg.get("database"),
                    "user": cfg.get("user"),
                    "password": cfg.get("password"),
                    "schema": cfg.get("schema", "public"),
                }

        # 3️⃣ Si nada aplica → error claro
        raise RuntimeError(
            f"No se encontraron credenciales para el DataSource '{self.name}'. "
            f"Asegúrate de definirlo en settings.EXTERNAL_DBS o crear una ExternalConnection asociada."
        )


class UploadedDataset(models.Model):
    CSV = "csv"
    XLSX = "xlsx"
    SQL = "sql"
    FILE_TYPES = [
        (CSV, "CSV"),
        (XLSX, "Excel"),
        (SQL, "SQL"),
    ]

    source = models.OneToOneField(
        DataSource, on_delete=models.CASCADE, related_name="upload"
    )
    file = models.FileField(upload_to="uploads/")
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    rows_ingested = models.PositiveIntegerField(default=0)
    columns = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"Upload({self.source_id}) {self.file.name}"


class ExternalConnection(models.Model):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    DB_TYPES = [
        (POSTGRES, "PostgreSQL"),
        (MYSQL, "MySQL/MariaDB"),
    ]

    source = models.OneToOneField(
        DataSource, on_delete=models.CASCADE, related_name="connection"
    )
    db_type = models.CharField(max_length=20, choices=DB_TYPES, default=POSTGRES)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=5432)  # Puerto estándar PostgreSQL
    database = models.CharField(max_length=255)
    username = EncryptedCharField(max_length=255)
    password = EncryptedTextField()
    extras = models.JSONField(default=dict, blank=True)  # sslmode, schema, options, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"External({self.source_id}) {self.db_type}@{self.host}:{self.port}/{self.database}"


class Diagrama(models.Model):
    # Origen del diagrama
    AUTO = "AUTO"
    CHAT = "CHAT"
    SOURCE_CHOICES = [
        (AUTO, "Generado automáticamente"),
        (CHAT, "Generado por chat"),
    ]

    # Tipos de gráfico
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    SCATTER = "scatter"
    RADAR = "radar"
    AREA = "area"
    CHART_TYPES = [
        (BAR, "Barras"),
        (LINE, "Líneas"),
        (PIE, "Circular"),
        (DOUGHNUT, "Dona"),
        (SCATTER, "Dispersión"),
        (RADAR, "Radar"),
        (AREA, "Área"),
    ]

    # Relaciones
    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="diagramas"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Metadatos del diagrama
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Descripción generada por IA")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, default=BAR)
    source_type = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=AUTO)

    # Datos técnicos
    sql_query = models.TextField(help_text="Consulta SQL que genera los datos")
    chart_data = models.JSONField(help_text="Datos JSON para Chart.js {labels: [], datasets: []}")
    chart_config = models.JSONField(default=dict, help_text="Configuración específica del gráfico")

    # Control
    is_active = models.BooleanField(default=True, help_text="Si se muestra en el dashboard")
    order = models.PositiveIntegerField(default=0, help_text="Orden de visualización")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = "Diagrama"
        verbose_name_plural = "Diagramas"

    def __str__(self) -> str:
        return f"{self.title} ({self.data_source.name})"

    # ---------- helpers de visual ----------
    def get_chart_colors(self) -> list[str]:
        schemes = {
            "bar": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"],
            "line": ["#06b6d4", "#f97316", "#84cc16", "#ec4899", "#6366f1"],
            "pie": ["#f59e0b", "#ef4444", "#10b981", "#3b82f6", "#8b5cf6"],
            "area": ["#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
        }
        return schemes.get(self.chart_type, schemes["bar"])

    # ---------- acciones ----------
    def execute_query(self) -> dict:
        """
        Ejecuta self.sql_query contra la BD definida por el DataSource
        y actualiza self.chart_data en formato Chart.js.
        """
        try:
            engine = get_engine(**self.data_source.get_db_credentials())
            df = pd.read_sql(self.sql_query, engine)

            if df.shape[1] < 2:
                self.chart_data = {"labels": [], "datasets": []}
                self.save(update_fields=["chart_data", "updated_at"])
                return self.chart_data

            labels = df.iloc[:, 0].astype(str).tolist()
            # intenta valores numéricos
            values = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0).tolist()

            chart_data = {
                "labels": labels,
                "datasets": [{
                    "label": self.title,
                    "data": values,
                    "backgroundColor": self.get_chart_colors()[:len(labels)],
                    "borderColor": self.get_chart_colors()[:len(labels)],
                    "borderWidth": 2,
                }],
            }
            self.chart_data = chart_data
            self.save(update_fields=["chart_data", "updated_at"])
            return chart_data

        except Exception as e:
            # Devolvemos estructura válida con el error (útil para debug en UI)
            return {"error": str(e), "labels": [], "datasets": []}

    def duplicate(self, new_title: str | None = None) -> "Diagrama":
        """
        Crea una copia del diagrama actual.
        """
        copy = Diagrama.objects.create(
            data_source=self.data_source,
            owner=self.owner,
            title=new_title or f"{self.title} (Copia)",
            description=self.description,
            chart_type=self.chart_type,
            source_type=self.CHAT,  # las copias se marcan como del chat
            sql_query=self.sql_query,
            chart_data=(self.chart_data or {}).copy(),
            chart_config=(self.chart_config or {}).copy(),
            order=self.order + 1,
            is_active=True,
        )
        return copy
