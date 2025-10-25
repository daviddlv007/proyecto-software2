"""
Servicio de detección de anomalías (ML Semi-Supervisado)
Isolation Forest con sklearn
"""
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sqlalchemy.orm import Session
from app.database import VentaCache, ModelMetadata
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Cache del modelo
_model_cache = {
    "model": None,
    "scaler": None,
    "trained_at": None
}


def train_anomaly_detector(db: Session):
    """
    Entrena detector de anomalías con Isolation Forest
    Features: total, num_productos
    """
    logger.info("🔍 Entrenando detector de anomalías...")
    
    # Obtener ventas
    ventas = db.query(VentaCache).all()
    
    if len(ventas) < 20:
        logger.warning("⚠️ Pocas ventas para entrenar (mínimo 20)")
        return None
    
    # Preparar dataset
    data = []
    for v in ventas:
        # Calcular ticket promedio por producto
        ticket_prom = v.total / v.num_productos if v.num_productos > 0 else 0
        
        data.append({
            "venta_id": v.id,
            "total": v.total,
            "num_productos": v.num_productos,
            "ticket_promedio": ticket_prom
        })
    
    df = pd.DataFrame(data)
    
    # Features
    X = df[["total", "num_productos", "ticket_promedio"]]
    
    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Entrenar Isolation Forest
    # contamination=0.1 significa que esperamos ~10% de anomalías
    iso_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    iso_forest.fit(X_scaled)
    
    # Guardar en caché
    _model_cache["model"] = iso_forest
    _model_cache["scaler"] = scaler
    _model_cache["trained_at"] = datetime.utcnow()
    
    # Guardar metadata
    metadata = db.query(ModelMetadata).filter_by(model_name="anomaly_detector").first()
    if not metadata:
        metadata = ModelMetadata(
            model_name="anomaly_detector",
            trained_at=datetime.utcnow(),
            accuracy=None,
            samples_count=len(ventas),
            features='["total", "num_productos", "ticket_promedio"]'
        )
        db.add(metadata)
    else:
        metadata.trained_at = datetime.utcnow()
        metadata.samples_count = len(ventas)
    
    db.commit()
    
    logger.info(f"✅ Detector entrenado con {len(ventas)} ventas")
    
    return {
        "samples": len(ventas)
    }


def detect_anomalies(db: Session):
    """
    Detecta ventas anómalas
    Retorna lista de anomalías con score
    """
    if _model_cache["model"] is None:
        raise ValueError("Modelo no entrenado. Ejecuta /sync primero.")
    
    model = _model_cache["model"]
    scaler = _model_cache["scaler"]
    
    # Obtener ventas
    ventas = db.query(VentaCache).all()
    
    # Preparar dataset
    data = []
    for v in ventas:
        ticket_prom = v.total / v.num_productos if v.num_productos > 0 else 0
        
        data.append({
            "venta_id": v.id,
            "fecha": v.fecha,
            "total": v.total,
            "num_productos": v.num_productos,
            "ticket_promedio": ticket_prom
        })
    
    df = pd.DataFrame(data)
    
    # Features
    X = df[["total", "num_productos", "ticket_promedio"]]
    X_scaled = scaler.transform(X)
    
    # Predecir anomalías
    # -1 = anomalía, 1 = normal
    predictions = model.predict(X_scaled)
    
    # Calcular score de anomalía (más negativo = más anómalo)
    scores = model.score_samples(X_scaled)
    
    df["is_anomaly"] = predictions
    df["anomaly_score"] = scores
    
    # Filtrar solo anomalías
    anomalias = df[df["is_anomaly"] == -1].copy()
    
    # Determinar razón de anomalía
    def get_razon(row):
        razones = []
        if row["total"] > df["total"].quantile(0.95):
            razones.append("Total muy alto")
        if row["total"] < df["total"].quantile(0.05):
            razones.append("Total muy bajo")
        if row["num_productos"] > df["num_productos"].quantile(0.95):
            razones.append("Muchos productos")
        if row["num_productos"] == 0:
            razones.append("Sin productos")
        if row["ticket_promedio"] > df["ticket_promedio"].quantile(0.95):
            razones.append("Ticket promedio alto")
        
        return " | ".join(razones) if razones else "Patrón inusual"
    
    anomalias["razon"] = anomalias.apply(get_razon, axis=1)
    
    result = {
        "total_ventas_analizadas": len(ventas),
        "anomalias_detectadas": len(anomalias),
        "anomalias": []
    }
    
    for _, row in anomalias.iterrows():
        result["anomalias"].append({
            "venta_id": int(row["venta_id"]),
            "fecha": row["fecha"],
            "total": float(row["total"]),
            "score_anomalia": float(row["anomaly_score"]),
            "razon": row["razon"]
        })
    
    # Ordenar por score (más anómalas primero)
    result["anomalias"] = sorted(
        result["anomalias"],
        key=lambda x: x["score_anomalia"]
    )
    
    return result


def get_model_info(db: Session):
    """Obtiene información del modelo de anomalías"""
    metadata = db.query(ModelMetadata).filter_by(model_name="anomaly_detector").first()
    
    if metadata:
        return {
            "model_name": "anomaly_detector",
            "trained_at": metadata.trained_at,
            "accuracy": None,
            "samples_count": metadata.samples_count,
            "features": ["total", "num_productos", "ticket_promedio"]
        }
    
    return {
        "model_name": "anomaly_detector",
        "trained_at": None,
        "accuracy": None,
        "samples_count": 0,
        "features": []
    }
