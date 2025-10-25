-- ============================================
-- DL SERVICE - PostgreSQL Schema
-- Embeddings, modelos Deep Learning, cache
-- Schema minimalista, migrable, parametrizado
-- ============================================

-- ============================================
-- EMBEDDINGS DE PRODUCTOS (Autoencoder output)
-- ============================================
CREATE TABLE IF NOT EXISTS product_embeddings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    
    -- Embedding vector (almacenado como JSONB para flexibilidad)
    -- En producción podría ser pgvector extension
    embedding JSONB NOT NULL,
    embedding_dim INTEGER NOT NULL DEFAULT 32,
    
    -- Metadata del modelo que generó el embedding
    model_version VARCHAR(20) DEFAULT '1.0',
    trained_at TIMESTAMP,
    
    -- Para invalidación de cache
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_product ON product_embeddings(product_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_updated ON product_embeddings(updated_at);
CREATE INDEX IF NOT EXISTS idx_embeddings_version ON product_embeddings(model_version);

-- ============================================
-- MATRIZ DE CO-COMPRA (para Collaborative Filtering)
-- ============================================
CREATE TABLE IF NOT EXISTS copurchase_matrix (
    id SERIAL PRIMARY KEY,
    product_a INTEGER NOT NULL,
    product_b INTEGER NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    confidence DECIMAL(5, 4), -- Lift, support, etc.
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_a, product_b)
);

CREATE INDEX IF NOT EXISTS idx_copurchase_a ON copurchase_matrix(product_a);
CREATE INDEX IF NOT EXISTS idx_copurchase_b ON copurchase_matrix(product_b);
CREATE INDEX IF NOT EXISTS idx_copurchase_count ON copurchase_matrix(count DESC);

-- ============================================
-- MODELOS DEEP LEARNING (metadata)
-- ============================================
CREATE TABLE IF NOT EXISTS dl_models (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'image_classification', 'lstm_forecasting', 'autoencoder_embeddings'
    version VARCHAR(20) NOT NULL,
    arquitectura VARCHAR(100), -- 'MobileNetV2', 'LSTM', 'Autoencoder'
    
    -- Configuración del modelo
    configuracion JSONB,
    
    -- Métricas de entrenamiento
    loss DECIMAL(10, 6),
    accuracy DECIMAL(5, 4),
    val_loss DECIMAL(10, 6),
    val_accuracy DECIMAL(5, 4),
    
    -- Metadata
    num_epochs INTEGER,
    num_parameters INTEGER,
    input_shape JSONB,
    output_shape JSONB,
    
    fecha_entrenamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    
    -- Path al modelo (migrable a cloud storage)
    modelo_path VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(nombre, version)
);

CREATE INDEX IF NOT EXISTS idx_dl_models_tipo ON dl_models(tipo);
CREATE INDEX IF NOT EXISTS idx_dl_models_activo ON dl_models(activo);
CREATE INDEX IF NOT EXISTS idx_dl_models_fecha ON dl_models(fecha_entrenamiento);

-- ============================================
-- PREDICCIONES LSTM (cache de forecasts)
-- ============================================
CREATE TABLE IF NOT EXISTS sales_predictions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES dl_models(id) ON DELETE CASCADE,
    product_id INTEGER, -- NULL para predicciones globales
    
    -- Serie temporal predicha
    prediction_data JSONB NOT NULL, -- [{fecha, valor, confidence}, ...]
    horizon_days INTEGER NOT NULL, -- Ventana de predicción
    
    -- Metadata
    confidence DECIMAL(5, 4),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP, -- TTL para invalidación
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_product ON sales_predictions(product_id);
CREATE INDEX IF NOT EXISTS idx_predictions_valid ON sales_predictions(valid_until);
CREATE INDEX IF NOT EXISTS idx_predictions_generated ON sales_predictions(generated_at);

-- ============================================
-- IDENTIFICACIONES DE PRODUCTOS (via imagen)
-- ============================================
CREATE TABLE IF NOT EXISTS product_identifications (
    id SERIAL PRIMARY KEY,
    image_hash VARCHAR(64) NOT NULL, -- Hash de la imagen para deduplicación
    
    -- Resultado de la identificación
    product_id INTEGER,
    confidence DECIMAL(5, 4) NOT NULL,
    
    -- Metadata de la imagen
    image_path VARCHAR(500), -- Path temporal o en storage
    image_size_bytes INTEGER,
    
    -- Modelo usado
    model_id INTEGER REFERENCES dl_models(id) ON DELETE SET NULL,
    
    -- Predicciones alternativas (top-3)
    alternatives JSONB, -- [{product_id, confidence}, ...]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_identifications_hash ON product_identifications(image_hash);
CREATE INDEX IF NOT EXISTS idx_identifications_product ON product_identifications(product_id);
CREATE INDEX IF NOT EXISTS idx_identifications_date ON product_identifications(created_at);

-- ============================================
-- SINCRONIZACIONES CON CORE SERVICE
-- ============================================
CREATE TABLE IF NOT EXISTS sync_status (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL, -- 'productos', 'ventas', 'embeddings'
    num_registros INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'EXITOSA',
    mensaje TEXT,
    fecha_sincronizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracion_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_tipo ON sync_status(tipo);
CREATE INDEX IF NOT EXISTS idx_sync_fecha ON sync_status(fecha_sincronizacion);

-- ============================================
-- TRIGGERS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_embeddings_updated_at BEFORE UPDATE ON product_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_copurchase_updated_at BEFORE UPDATE ON copurchase_matrix
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dl_models_updated_at BEFORE UPDATE ON dl_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- FUNCIONES DE UTILIDAD
-- ============================================

-- Función para limpiar predicciones expiradas
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS TABLE(predictions_deleted INTEGER, old_identifications_deleted INTEGER) AS $$
DECLARE
    pred_count INTEGER;
    ident_count INTEGER;
BEGIN
    -- Limpiar predicciones expiradas
    DELETE FROM sales_predictions 
    WHERE valid_until IS NOT NULL AND valid_until < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS pred_count = ROW_COUNT;
    
    -- Limpiar identificaciones antiguas (>30 días)
    DELETE FROM product_identifications 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    GET DIAGNOSTICS ident_count = ROW_COUNT;
    
    RETURN QUERY SELECT pred_count, ident_count;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular similitud coseno (para búsqueda de embeddings similares)
-- En producción se recomienda usar pgvector extension
CREATE OR REPLACE FUNCTION cosine_similarity(vec1 JSONB, vec2 JSONB)
RETURNS DECIMAL AS $$
DECLARE
    dot_product DECIMAL := 0;
    mag1 DECIMAL := 0;
    mag2 DECIMAL := 0;
    i INTEGER;
    len INTEGER;
BEGIN
    len := jsonb_array_length(vec1);
    
    FOR i IN 0..len-1 LOOP
        dot_product := dot_product + 
            (vec1->>i)::DECIMAL * (vec2->>i)::DECIMAL;
        mag1 := mag1 + POWER((vec1->>i)::DECIMAL, 2);
        mag2 := mag2 + POWER((vec2->>i)::DECIMAL, 2);
    END LOOP;
    
    IF mag1 = 0 OR mag2 = 0 THEN
        RETURN 0;
    END IF;
    
    RETURN dot_product / (SQRT(mag1) * SQRT(mag2));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- DATOS DE PRUEBA (comentar en producción)
-- ============================================

-- Modelo MobileNet (pre-entrenado)
INSERT INTO dl_models (
    nombre, tipo, version, arquitectura,
    configuracion, activo, modelo_path
) VALUES (
    'mobilenet_v2',
    'image_classification',
    '2.1.0',
    'MobileNetV2',
    '{"input_size": [224, 224, 3], "pretrained": true, "classes": 1000}'::jsonb,
    true,
    '@tensorflow-models/mobilenet'
) ON CONFLICT (nombre, version) DO NOTHING;

-- Modelo LSTM para predicción de ventas
INSERT INTO dl_models (
    nombre, tipo, version, arquitectura,
    configuracion, num_epochs, activo
) VALUES (
    'lstm_sales_predictor',
    'lstm_forecasting',
    '1.0.0',
    'LSTM',
    '{"units": 16, "dropout": 0.2, "window_size": 7, "horizon": 7}'::jsonb,
    50,
    true
) ON CONFLICT (nombre, version) DO NOTHING;

-- Modelo Autoencoder para embeddings
INSERT INTO dl_models (
    nombre, tipo, version, arquitectura,
    configuracion, num_epochs, activo
) VALUES (
    'product_autoencoder',
    'autoencoder_embeddings',
    '1.0.0',
    'Autoencoder',
    '{"embedding_dim": 32, "activation": "relu"}'::jsonb,
    30,
    true
) ON CONFLICT (nombre, version) DO NOTHING;

-- Comentario: Schema listo para producción
-- Usar DATABASE_URL en .env
-- Embeddings pueden migrarse a pgvector en producción
-- Paths de modelos migrables a S3/GCS
