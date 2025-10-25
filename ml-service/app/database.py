"""
Base de datos para ML Service
Soporta SQLite (desarrollo) y PostgreSQL (Docker/producción)
Configurado via DATABASE_URL environment variable
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Obtener DATABASE_URL desde environment (migrable a producción)
# Formato: postgresql://user:pass@host:port/dbname
# Fallback a SQLite para desarrollo local
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./ml_cache.db"
)

# Configuración del engine según tipo de BD
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verificar conexión antes de usar
        pool_recycle=3600    # Reciclar conexiones cada hora
    )
else:
    # SQLite
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ===================================
# MODELOS DE CACHÉ (esquema mínimo)
# ===================================

class ProductoCache(Base):
    """Snapshot de productos para features ML"""
    __tablename__ = "productos_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    categoria = Column(String)
    precio = Column(Float)
    stock = Column(Integer)
    synced_at = Column(DateTime, default=datetime.utcnow)


class VentaCache(Base):
    """Snapshot de ventas para entrenamiento"""
    __tablename__ = "ventas_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, index=True)
    fecha = Column(String)
    total = Column(Float)
    num_productos = Column(Integer)
    synced_at = Column(DateTime, default=datetime.utcnow)


class ClienteMetrics(Base):
    """Métricas agregadas por cliente para clustering"""
    __tablename__ = "cliente_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, unique=True, index=True)
    nombre = Column(String)
    total_compras = Column(Float, default=0.0)
    frecuencia = Column(Integer, default=0)
    ticket_promedio = Column(Float, default=0.0)
    segmento = Column(String, nullable=True)  # VIP, Regular, Ocasional
    updated_at = Column(DateTime, default=datetime.utcnow)


class ModelMetadata(Base):
    """Metadata de modelos entrenados"""
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, unique=True)
    trained_at = Column(DateTime)
    accuracy = Column(Float, nullable=True)
    samples_count = Column(Integer)
    features = Column(String)  # JSON string


# Crear tablas
Base.metadata.create_all(bind=engine)


# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
