"""
ML Service - Microservicio de Machine Learning
FastAPI + scikit-learn + SQLite

Endpoints REST para:
- Predicción de precios (Supervisado)
- Segmentación de clientes (No Supervisado)
- Detección de anomalías (Semi-Supervisado)
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.database import get_db, ProductoCache, VentaCache, ClienteMetrics
from app.schemas import (
    PredictPriceRequest, PredictPriceResponse,
    SegmentacionResponse, AnomaliesResponse,
    SyncResponse, HealthResponse, ModelsResponse
)
from app.services import data_sync, predictor, segmentacion, anomalias

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="ML Service - Supermercado",
    description="Microservicio de Machine Learning para análisis predictivo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir requests desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================
# ENDPOINTS DE GESTIÓN
# ===================================

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz"""
    return {
        "service": "ML Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "sync": "/sync",
            "predict_price": "/predict/price",
            "segmentation": "/ml/segmentacion",
            "anomalies": "/ml/anomalias"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check del servicio
    Verifica conectividad con core-service y estado de modelos
    """
    core_reachable = await data_sync.check_core_service_health()
    
    # Verificar si hay datos en caché
    productos_count = db.query(ProductoCache).count()
    ventas_count = db.query(VentaCache).count()
    clientes_count = db.query(ClienteMetrics).count()
    
    models_trained = productos_count > 0 and ventas_count > 0
    
    return {
        "status": "healthy" if core_reachable else "degraded",
        "service": "ml-service",
        "core_service_reachable": core_reachable,
        "models_trained": models_trained,
        "cache_size": {
            "productos": productos_count,
            "ventas": ventas_count,
            "clientes": clientes_count
        }
    }


@app.post("/sync", response_model=SyncResponse, tags=["Data Management"])
async def sync_data(db: Session = Depends(get_db)):
    """
    Sincroniza datos desde core-service y entrena modelos
    
    Pasos:
    1. Consulta datos via GraphQL desde core-service
    2. Almacena en caché local (SQLite)
    3. Entrena los 3 modelos ML:
       - Predicción de precios (Supervisado)
       - Segmentación de clientes (No Supervisado)
       - Detección de anomalías (Semi-Supervisado)
    """
    logger.info("📥 Iniciando sincronización completa...")
    
    try:
        # Sincronizar datos
        sync_result = await data_sync.sync_data(db)
        
        # Entrenar modelos
        logger.info("🤖 Entrenando modelos ML...")
        
        predictor.train_price_predictor(db)
        segmentacion.train_segmentation(db)
        anomalias.train_anomaly_detector(db)
        
        logger.info("✅ Sincronización y entrenamiento completados")
        
        return sync_result
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        raise HTTPException(status_code=500, detail=f"Error en sync: {str(e)}")


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def get_models_info(db: Session = Depends(get_db)):
    """
    Obtiene información de todos los modelos entrenados
    """
    models = [
        predictor.get_model_info(db),
        segmentacion.get_model_info(db),
        anomalias.get_model_info(db)
    ]
    
    return {"models": models}


# ===================================
# ENDPOINTS DE ML
# ===================================

@app.post("/predict/price", response_model=PredictPriceResponse, tags=["ML - Supervisado"])
async def predict_price(request: PredictPriceRequest):
    """
    Predice el precio de un producto usando Regresión Lineal
    
    **Features usadas:**
    - Categoría del producto
    - Stock disponible
    - Longitud del nombre
    
    **Algoritmo:** LinearRegression (sklearn)
    
    **Uso:** Sugerir precios para nuevos productos
    """
    try:
        result = predictor.predict_price(
            categoria=request.categoria,
            stock=request.stock,
            nombre=request.nombre
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/ml/segmentacion", response_model=SegmentacionResponse, tags=["ML - No Supervisado"])
async def get_segmentacion(db: Session = Depends(get_db)):
    """
    Obtiene la segmentación de clientes usando K-Means
    
    **Features usadas:**
    - Total de compras
    - Frecuencia de compras
    - Ticket promedio
    
    **Algoritmo:** K-Means (3 clusters: VIP, Regular, Ocasional)
    
    **Uso:** Identificar clientes VIP para campañas de marketing
    """
    try:
        result = segmentacion.get_segmentation(db)
        return result
    except Exception as e:
        logger.error(f"Error en segmentación: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/ml/anomalias", response_model=AnomaliesResponse, tags=["ML - Semi-Supervisado"])
async def get_anomalias(db: Session = Depends(get_db)):
    """
    Detecta ventas anómalas usando Isolation Forest
    
    **Features usadas:**
    - Total de la venta
    - Número de productos
    - Ticket promedio por producto
    
    **Algoritmo:** Isolation Forest (sklearn)
    
    **Uso:** Detectar posibles fraudes o errores de captura
    """
    try:
        result = anomalias.detect_anomalies(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en detección de anomalías: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ===================================
# STARTUP EVENT
# ===================================

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio
    Crea las tablas de BD si no existen
    """
    logger.info("🚀 ML Service iniciando...")
    logger.info("📊 Base de datos SQLite inicializada")
    logger.info("✅ Servicio listo en http://localhost:8081")
    logger.info("📖 Documentación en http://localhost:8081/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
