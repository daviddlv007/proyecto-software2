"""
Servicio de segmentación de clientes (ML No Supervisado)
K-Means clustering con sklearn
"""
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sqlalchemy.orm import Session
from app.database import ClienteMetrics, ModelMetadata
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Cache del modelo
_model_cache = {
    "model": None,
    "scaler": None,
    "trained_at": None
}


def train_segmentation(db: Session):
    """
    Entrena modelo de clustering K-Means
    Features: total_compras, frecuencia, ticket_promedio
    3 clusters: VIP, Regular, Ocasional
    """
    logger.info("🎯 Entrenando modelo de segmentación de clientes...")
    
    # Obtener métricas de clientes
    clientes = db.query(ClienteMetrics).all()
    
    if len(clientes) < 5:
        logger.warning("⚠️ Pocos clientes para clustering (mínimo 5)")
        return None
    
    # Preparar dataset
    data = []
    for c in clientes:
        data.append({
            "cliente_id": c.cliente_id,
            "total_compras": c.total_compras,
            "frecuencia": c.frecuencia,
            "ticket_promedio": c.ticket_promedio
        })
    
    df = pd.DataFrame(data)
    
    # Features para clustering
    X = df[["total_compras", "frecuencia", "ticket_promedio"]]
    
    # Escalar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Entrenar K-Means (3 clusters)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    # Asignar etiquetas
    df["cluster"] = kmeans.labels_
    
    # Mapear clusters a segmentos interpretables
    # Cluster con mayor ticket promedio = VIP
    cluster_means = df.groupby("cluster")["ticket_promedio"].mean()
    sorted_clusters = cluster_means.sort_values(ascending=False).index.tolist()
    
    cluster_map = {
        sorted_clusters[0]: "VIP",
        sorted_clusters[1]: "Regular",
        sorted_clusters[2]: "Ocasional"
    }
    
    df["segmento"] = df["cluster"].map(cluster_map)
    
    # Actualizar segmentos en BD
    for _, row in df.iterrows():
        cliente = db.query(ClienteMetrics).filter_by(cliente_id=int(row["cliente_id"])).first()
        if cliente:
            cliente.segmento = row["segmento"]
            cliente.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Guardar en caché
    _model_cache["model"] = kmeans
    _model_cache["scaler"] = scaler
    _model_cache["trained_at"] = datetime.utcnow()
    
    # Guardar metadata
    metadata = db.query(ModelMetadata).filter_by(model_name="customer_segmentation").first()
    if not metadata:
        metadata = ModelMetadata(
            model_name="customer_segmentation",
            trained_at=datetime.utcnow(),
            accuracy=None,  # clustering no tiene accuracy tradicional
            samples_count=len(clientes),
            features='["total_compras", "frecuencia", "ticket_promedio"]'
        )
        db.add(metadata)
    else:
        metadata.trained_at = datetime.utcnow()
        metadata.samples_count = len(clientes)
    
    db.commit()
    
    # Stats
    vip_count = sum(df["segmento"] == "VIP")
    regular_count = sum(df["segmento"] == "Regular")
    ocasional_count = sum(df["segmento"] == "Ocasional")
    
    logger.info(f"✅ Segmentación completada:")
    logger.info(f"   - VIP: {vip_count}")
    logger.info(f"   - Regulares: {regular_count}")
    logger.info(f"   - Ocasionales: {ocasional_count}")
    
    return {
        "vip_count": vip_count,
        "regular_count": regular_count,
        "ocasional_count": ocasional_count
    }


def get_segmentation(db: Session):
    """
    Obtiene la segmentación actual de todos los clientes
    """
    clientes = db.query(ClienteMetrics).all()
    
    result = {
        "total_clientes": len(clientes),
        "vip_count": 0,
        "regular_count": 0,
        "ocasional_count": 0,
        "clientes": []
    }
    
    for c in clientes:
        if c.segmento == "VIP":
            result["vip_count"] += 1
        elif c.segmento == "Regular":
            result["regular_count"] += 1
        elif c.segmento == "Ocasional":
            result["ocasional_count"] += 1
        
        result["clientes"].append({
            "cliente_id": c.cliente_id,
            "nombre": c.nombre,
            "segmento": c.segmento or "Sin clasificar",
            "total_compras": c.total_compras,
            "frecuencia": c.frecuencia,
            "ticket_promedio": c.ticket_promedio
        })
    
    return result


def get_model_info(db: Session):
    """Obtiene información del modelo de segmentación"""
    metadata = db.query(ModelMetadata).filter_by(model_name="customer_segmentation").first()
    
    if metadata:
        return {
            "model_name": "customer_segmentation",
            "trained_at": metadata.trained_at,
            "accuracy": None,
            "samples_count": metadata.samples_count,
            "features": ["total_compras", "frecuencia", "ticket_promedio"]
        }
    
    return {
        "model_name": "customer_segmentation",
        "trained_at": None,
        "accuracy": None,
        "samples_count": 0,
        "features": []
    }
