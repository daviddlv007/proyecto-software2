from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.urls import reverse
from .models import DataSource, UploadedDataset, Diagrama
from .services import (
    import_csv_or_excel, import_sql_script, sanitize_identifier, get_dataset, 
    get_schema_info, generar_consulta_y_grafico, generar_diagramas_automaticos,
    generar_diagrama_chat, guardar_diagrama, obtener_diagramas_por_archivo
)
import json
import uuid
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db import connection
from django.http import HttpResponse  
from django.conf import settings
import subprocess
import tempfile
from django.http import FileResponse
import os
from sqlalchemy import text
from .services import get_engine
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .services import get_schema_info, generar_consulta_y_grafico, reduce_schema
from django.core.mail import EmailMessage
from datetime import datetime
import base64
from django.views.decorators.http import require_GET
from .services import analyze_chart_image

def api_list_datasets(request, user_id):
    datasets = DataSource.objects.filter(owner_id=user_id).order_by("-created_at")
    data = [
        {
            "id": ds.id,
            "name": ds.name or "Sin nombre",
            "schema": ds.internal_schema or "",
            "table": ds.internal_table or "",
            "created_at": ds.created_at.strftime("%Y-%m-%d %H:%M:%S") if ds.created_at else "",
        }
        for ds in datasets
    ]
    return JsonResponse({"datasets": data})




def diagramas_por_data_source(request, data_source_id):
    """
    Devuelve todos los diagramas asociados a un DataSource específico.
    """
    try:
        # Filtra por data_source_id y solo los activos
        diagramas = Diagrama.objects.filter(
            data_source_id=data_source_id,
            is_active=True
        ).order_by("order", "created_at")

        # Serializa la información en JSON
        data = [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "chart_type": d.chart_type,
                "source_type": d.source_type,
                "sql_query": d.sql_query,
                "chart_data": d.chart_data,
                "order": d.order,
                "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for d in diagramas
        ]

        return JsonResponse({"status": "ok", "diagramas": data}, status=200)

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)}, status=500
        )