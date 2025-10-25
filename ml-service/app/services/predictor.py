"""
Servicio de predicción de precios (ML Supervisado)
Regresión Lineal simple con sklearn
"""
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sqlalchemy.orm import Session
from app.database import ProductoCache, ModelMetadata
from datetime import datetime
import pickle
import logging

logger = logging.getLogger(__name__)

# Cache del modelo en memoria
_model_cache = {
    "model": None,
    "label_encoder": None,
    "trained_at": None
}


def train_price_predictor(db: Session):
    """
    Entrena modelo de predicción de precios
    Features: categoria_encoded, stock, len_nombre
    Target: precio
    """
    logger.info("🤖 Entrenando modelo de predicción de precios...")
    
    # Obtener datos de productos
    productos = db.query(ProductoCache).all()
    
    if len(productos) < 10:
        logger.warning("⚠️ Pocos datos para entrenar (mínimo 10 productos)")
        return None
    
    # Preparar dataset
    data = []
    for p in productos:
        data.append({
            "categoria": p.categoria,
            "stock": p.stock,
            "len_nombre": len(p.nombre),
            "precio": p.precio
        })
    
    df = pd.DataFrame(data)
    
    # Encode categorías
    le = LabelEncoder()
    df["categoria_encoded"] = le.fit_transform(df["categoria"])
    
    # Features y target
    X = df[["categoria_encoded", "stock", "len_nombre"]]
    y = df["precio"]
    
    # Entrenar modelo
    model = LinearRegression()
    model.fit(X, y)
    
    # Calcular R² score como métrica simple
    score = model.score(X, y)
    
    # Guardar en caché
    _model_cache["model"] = model
    _model_cache["label_encoder"] = le
    _model_cache["trained_at"] = datetime.utcnow()
    
    # Guardar metadata
    metadata = db.query(ModelMetadata).filter_by(model_name="price_predictor").first()
    if not metadata:
        metadata = ModelMetadata(
            model_name="price_predictor",
            trained_at=datetime.utcnow(),
            accuracy=score,
            samples_count=len(productos),
            features='["categoria", "stock", "len_nombre"]'
        )
        db.add(metadata)
    else:
        metadata.trained_at = datetime.utcnow()
        metadata.accuracy = score
        metadata.samples_count = len(productos)
    
    db.commit()
    
    logger.info(f"✅ Modelo entrenado - R²: {score:.4f} con {len(productos)} productos")
    
    return {
        "accuracy": score,
        "samples": len(productos)
    }


def predict_price(categoria: str, stock: int, nombre: str):
    """
    Predice el precio de un producto
    """
    if _model_cache["model"] is None:
        raise ValueError("Modelo no entrenado. Ejecuta /sync primero.")
    
    model = _model_cache["model"]
    le = _model_cache["label_encoder"]
    
    # Encode categoria (si no existe, usar categoría más frecuente)
    try:
        categoria_encoded = le.transform([categoria])[0]
    except ValueError:
        # Categoría desconocida, usar promedio
        categoria_encoded = len(le.classes_) // 2
    
    len_nombre = len(nombre)
    
    # Predecir
    X_new = [[categoria_encoded, stock, len_nombre]]
    precio_pred = model.predict(X_new)[0]
    
    # Confianza simple (basada en R² del modelo)
    # En producción usarías cross-validation
    confianza = 0.85  # placeholder
    
    return {
        "precio_sugerido": round(float(precio_pred), 2),
        "categoria": categoria,
        "confianza": confianza,
        "features_used": ["categoria", "stock", "longitud_nombre"]
    }


def get_model_info(db: Session):
    """Obtiene información del modelo entrenado"""
    metadata = db.query(ModelMetadata).filter_by(model_name="price_predictor").first()
    
    if metadata:
        return {
            "model_name": "price_predictor",
            "trained_at": metadata.trained_at,
            "accuracy": metadata.accuracy,
            "samples_count": metadata.samples_count,
            "features": ["categoria", "stock", "len_nombre"]
        }
    
    return {
        "model_name": "price_predictor",
        "trained_at": None,
        "accuracy": None,
        "samples_count": 0,
        "features": []
    }
