"""
Pydantic schemas para validación de requests/responses
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ===================================
# REQUEST SCHEMAS
# ===================================

class PredictPriceRequest(BaseModel):
    """Request para predicción de precio"""
    categoria: str
    stock: int
    nombre: str


class SegmentClienteRequest(BaseModel):
    """Request para segmentación manual de un cliente"""
    cliente_id: int


# ===================================
# RESPONSE SCHEMAS
# ===================================

class PredictPriceResponse(BaseModel):
    """Response de predicción de precio"""
    precio_sugerido: float
    categoria: str
    confianza: float
    features_used: List[str]


class ClienteSegment(BaseModel):
    """Segmento de un cliente"""
    cliente_id: int
    nombre: str
    segmento: str  # VIP, Regular, Ocasional
    total_compras: float
    frecuencia: int
    ticket_promedio: float


class SegmentacionResponse(BaseModel):
    """Response de clustering completo"""
    total_clientes: int
    vip_count: int
    regular_count: int
    ocasional_count: int
    clientes: List[ClienteSegment]


class Anomalia(BaseModel):
    """Venta anómala detectada"""
    venta_id: int
    fecha: str
    total: float
    score_anomalia: float
    razon: str


class AnomaliesResponse(BaseModel):
    """Response de detección de anomalías"""
    total_ventas_analizadas: int
    anomalias_detectadas: int
    anomalias: List[Anomalia]


class SyncResponse(BaseModel):
    """Response de sincronización de datos"""
    productos_synced: int
    ventas_synced: int
    clientes_synced: int
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    core_service_reachable: bool
    models_trained: bool
    cache_size: dict


class ModelInfo(BaseModel):
    """Info de modelo entrenado"""
    model_name: str
    trained_at: Optional[datetime]
    accuracy: Optional[float]
    samples_count: int
    features: List[str]


class ModelsResponse(BaseModel):
    """Response con info de todos los modelos"""
    models: List[ModelInfo]
