"""
Módulo centralizado de configuración de conexiones a BD.
Configurable por variables de entorno para multi-instancia.
"""
import os
from django.conf import settings
from sqlalchemy import create_engine
from django.db import connections


def get_core_db_config():
    """
    Retorna configuración del core-service BD desde variables de entorno.
    Se usa en notificaciones, prep y otros módulos que necesitan acceder
    a datos del core-service (público).
    """
    return {
        'host': os.environ.get('CORE_DB_HOST', 'postgres'),
        'port': int(os.environ.get('CORE_DB_PORT', 5432)),
        'database': os.environ.get('CORE_DB_NAME', 'coredb'),
        'user': os.environ.get('CORE_DB_USER', 'postgres'),
        'password': os.environ.get('CORE_DB_PASSWORD', 'postgres'),
    }


def get_core_db_connection_string():
    """Retorna string de conexión PostgreSQL para core-service BD."""
    cfg = get_core_db_config()
    return f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"


def get_core_sqlalchemy_engine(echo=False):
    """
    Retorna engine SQLAlchemy para core-service BD.
    Úsalo en lugar de django.db.connection cuando necesites acceder
    a datos transaccionales del core-service.
    """
    return create_engine(get_core_db_connection_string(), echo=echo, future=True)


def get_bi_db_config():
    """
    Retorna configuración de BI-service BD (uso interno del BI).
    """
    return {
        'host': os.environ.get('BI_DB_HOST', 'localhost'),
        'port': int(os.environ.get('BI_DB_PORT', 5432)),
        'database': os.environ.get('BI_DB_NAME', 'software2_DB'),
        'user': os.environ.get('BI_DB_USER', 'postgres'),
        'password': os.environ.get('BI_DB_PASSWORD', 'postgres'),
    }


def get_core_raw_connection():
    """
    Retorna conexión raw de Django para core-service BD.
    Alternativa a psycopg2 directo cuando usas Django ORM.
    """
    core_db = get_core_db_config()
    # Registra la conexión en Django si no existe
    if 'core_db' not in connections.databases:
        connections.databases['core_db'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': core_db['database'],
            'USER': core_db['user'],
            'PASSWORD': core_db['password'],
            'HOST': core_db['host'],
            'PORT': core_db['port'],
        }
    return connections['core_db']
