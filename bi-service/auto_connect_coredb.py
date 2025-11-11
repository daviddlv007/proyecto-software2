#!/usr/bin/env python
"""
Script para auto-conectar coredb al BI Service al inicio
Crea automáticamente un DataSource apuntando a la BD core
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ingestion.models import DataSource, ExternalConnection
from django.contrib.auth.models import User

def auto_connect_coredb():
    """Crea conexión automática a coredb si no existe"""
    
    # Verificar si ya existe una conexión a coredb
    existing = DataSource.objects.filter(
        db_name='coredb',
        kind=DataSource.LIVE
    ).first()
    
    if existing:
        print(f"✅ Conexión a coredb ya existe (ID: {existing.id})")
        return existing
    
    # Obtener o crear usuario admin para el BI
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@localhost'
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Usuario admin creado")
    
    # Credenciales de coredb desde variables de entorno
    core_host = os.getenv('CORE_DB_HOST', 'postgres')
    core_port = int(os.getenv('CORE_DB_PORT', 5432))
    core_db = os.getenv('CORE_DB_NAME', 'coredb')
    core_user = os.getenv('CORE_DB_USER', 'postgres')
    core_password = os.getenv('CORE_DB_PASSWORD', 'postgres')
    
    # Crear DataSource
    ds = DataSource.objects.create(
        name="Core Database (Auto-conectado)",
        kind=DataSource.LIVE,
        owner=user,
        internal_schema="public",
        internal_table="",
        db_host=core_host,
        db_port=core_port,
        db_name=core_db,
        db_user=core_user,
        db_password=core_password,
    )
    
    # Crear ExternalConnection
    ExternalConnection.objects.create(
        source=ds,
        db_type=ExternalConnection.POSTGRES,
        host=core_host,
        port=core_port,
        database=core_db,
        username=core_user,
        password=core_password,
        extras={"schema": "public"},
    )
    
    print(f"✅ Conexión automática a coredb creada (ID: {ds.id})")
    print(f"   Host: {core_host}:{core_port}")
    print(f"   Database: {core_db}")
    print(f"   Schema: public")
    
    # Intentar generar diagramas automáticos para las tablas principales
    try:
        from ingestion.views import generar_diagramas_automaticos
        from sqlalchemy import inspect
        from ingestion.utils import get_engine
        
        creds = ds.get_db_credentials()
        engine = get_engine(**creds)
        insp = inspect(engine)
        tablas = insp.get_table_names(schema="public")
        
        # Filtrar solo tablas relevantes (evitar tablas de sistema)
        tablas_core = [t for t in tablas if t in ['ventas', 'clientes', 'productos', 'categorias', 'detalle_ventas', 'usuarios']]
        
        print(f"📊 Generando diagramas para {len(tablas_core)} tablas...")
        for tabla in tablas_core:
            ds.internal_table = tabla
            ds.save(update_fields=["internal_table"])
            try:
                generar_diagramas_automaticos(ds, **creds)
                print(f"   ✓ {tabla}")
            except Exception as e:
                print(f"   ⚠ {tabla}: {str(e)[:50]}")
        
        # Volver a dejar internal_table vacío
        ds.internal_table = ""
        ds.save(update_fields=["internal_table"])
        
    except Exception as e:
        print(f"⚠️ No se pudieron generar diagramas automáticos: {e}")
    
    return ds

if __name__ == '__main__':
    print("🔄 Configurando conexión automática a coredb...")
    auto_connect_coredb()
    print("✅ Configuración completada")
