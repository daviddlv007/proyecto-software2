-- ============================================
-- ML SERVICE - PostgreSQL Schema
-- Almacena modelos entrenados y métricas
-- Schema minimalista, migrable, sin hardcodeo
-- ============================================

-- ============================================
-- MODELOS ENTRENADOS (metadata)
-- ============================================
CREATE TABLE IF NOT EXISTS modelos_ml (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'clasificacion', 'prediccion', 'clustering'
    version VARCHAR(20) NOT NULL,
    algoritmo VARCHAR(100), -- 'RandomForest', 'XGBoost', 'LinearRegression'
    
    -- Configuración del modelo (JSON para flexibilidad)
    configuracion JSONB,
    
    -- Métricas de entrenamiento
    accuracy DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall_score DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    rmse DECIMAL(10, 4),
    
    -- Metadata
    num_features INTEGER,
    num_samples_train INTEGER,
    fecha_entrenamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    
    -- Path al archivo del modelo (para migración a S3/cloud storage)
    modelo_path VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(nombre, version)
);

CREATE INDEX IF NOT EXISTS idx_modelos_tipo ON modelos_ml(tipo);
CREATE INDEX IF NOT EXISTS idx_modelos_activo ON modelos_ml(activo);
CREATE INDEX IF NOT EXISTS idx_modelos_fecha ON modelos_ml(fecha_entrenamiento);

-- ============================================
-- PREDICCIONES (cache de resultados recientes)
-- ============================================
CREATE TABLE IF NOT EXISTS predicciones_cache (
    id SERIAL PRIMARY KEY,
    modelo_id INTEGER REFERENCES modelos_ml(id) ON DELETE CASCADE,
    input_hash VARCHAR(64) NOT NULL, -- Hash del input para cache
    input_data JSONB NOT NULL,
    resultado JSONB NOT NULL,
    confidence DECIMAL(5, 4),
    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl_expires_at TIMESTAMP, -- Time to live para auto-limpieza
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predicciones_modelo ON predicciones_cache(modelo_id);
CREATE INDEX IF NOT EXISTS idx_predicciones_hash ON predicciones_cache(input_hash);
CREATE INDEX IF NOT EXISTS idx_predicciones_ttl ON predicciones_cache(ttl_expires_at);

-- ============================================
-- SINCRONIZACIONES (tracking de sync con Core Service)
-- ============================================
CREATE TABLE IF NOT EXISTS sincronizaciones (
    id SERIAL PRIMARY KEY,
    servicio_origen VARCHAR(50) NOT NULL, -- 'core-service'
    tipo VARCHAR(50) NOT NULL, -- 'productos', 'ventas', 'clientes'
    num_registros INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'EXITOSA', -- 'EXITOSA', 'FALLIDA', 'PARCIAL'
    mensaje TEXT,
    fecha_sincronizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracion_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_tipo ON sincronizaciones(tipo);
CREATE INDEX IF NOT EXISTS idx_sync_fecha ON sincronizaciones(fecha_sincronizacion);
CREATE INDEX IF NOT EXISTS idx_sync_estado ON sincronizaciones(estado);

-- ============================================
-- FEATURES ENGINEERING (cache de features calculados)
-- ============================================
CREATE TABLE IF NOT EXISTS features_cache (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'producto', 'cliente', 'venta'
    entity_id INTEGER NOT NULL,
    features JSONB NOT NULL, -- Flexible para cualquier feature
    version VARCHAR(20) DEFAULT '1.0',
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(entity_type, entity_id, version)
);

CREATE INDEX IF NOT EXISTS idx_features_type_id ON features_cache(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_features_fecha ON features_cache(fecha_calculo);

-- ============================================
-- TRIGGERS para updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_modelos_updated_at BEFORE UPDATE ON modelos_ml
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- FUNCIONES DE LIMPIEZA AUTOMÁTICA
-- ============================================

-- Función para limpiar predicciones expiradas
CREATE OR REPLACE FUNCTION cleanup_expired_predictions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM predicciones_cache 
    WHERE ttl_expires_at IS NOT NULL 
      AND ttl_expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DATOS DE PRUEBA (comentar en producción)
-- ============================================

-- Modelo de ejemplo
INSERT INTO modelos_ml (
    nombre, tipo, version, algoritmo, 
    configuracion, accuracy, num_features, num_samples_train,
    activo, modelo_path
) VALUES (
    'clasificador_productos', 
    'clasificacion', 
    '1.0.0', 
    'RandomForest',
    '{"n_estimators": 100, "max_depth": 10}'::jsonb,
    0.9245,
    15,
    1000,
    true,
    '/models/clasificador_productos_v1.pkl'
) ON CONFLICT (nombre, version) DO NOTHING;

-- Comentario: Este esquema es migrable a producción
-- Variables de configuración deben estar en .env
-- Paths de modelos pueden migrarse a S3/GCS/Azure Blob
