-- ============================================
-- CORE SERVICE - PostgreSQL Schema (FULL)
-- Incluye Payments + Delivery en "ventas"
-- Idempotente (CREATE IF NOT EXISTS + ALTER condicional)
-- Compatible PostgreSQL 12+
-- ============================================

-- Extensiones útiles (opcional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CATEGORÍAS
-- ============================================
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categorias_nombre ON categorias(nombre);
CREATE INDEX IF NOT EXISTS idx_categorias_activa ON categorias(activa);

-- ============================================
-- PRODUCTOS   
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL CHECK (precio >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    imagen_url VARCHAR(500),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_productos_nombre   ON productos(nombre);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_productos_activo   ON productos(activo);
CREATE INDEX IF NOT EXISTS idx_productos_precio   ON productos(precio);

-- ============================================
-- CLIENTES
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    direccion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);
CREATE INDEX IF NOT EXISTS idx_clientes_activo ON clientes(activo);

-- ============================================
-- USUARIOS (autenticación)
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'USER',
    activo BOOLEAN DEFAULT true,
    ultimo_acceso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol      ON usuarios(rol);

-- ============================================
-- VENTAS (con Payments + Delivery)
-- ============================================
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE SET NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    estado VARCHAR(20) DEFAULT 'COMPLETADA',
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,

    -- ===== Payments (NULL-ables) =====
    payment_provider     VARCHAR(20),
    payment_status       VARCHAR(20),
    checkout_session_id  VARCHAR(100),
    payment_intent_id    VARCHAR(100),
    qr_checkout_url      TEXT,
    currency             VARCHAR(10) DEFAULT 'USD',

    -- ===== Delivery (NULL-ables) =====
    delivery_status       VARCHAR(20),
    delivery_address      TEXT,
    delivery_lat          DOUBLE PRECISION,
    delivery_lng          DOUBLE PRECISION,
    delivery_distance_km  DOUBLE PRECISION,
    delivery_fee          DOUBLE PRECISION,
    delivery_eta_minutes  INTEGER,
    delivery_rider_id     VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Si la tabla "ventas" ya existía sin columnas nuevas, agrégalas (idempotente)
DO $$
BEGIN
  -- Payments
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='payment_provider') THEN
    ALTER TABLE public.ventas ADD COLUMN payment_provider VARCHAR(20);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='payment_status') THEN
    ALTER TABLE public.ventas ADD COLUMN payment_status VARCHAR(20);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='checkout_session_id') THEN
    ALTER TABLE public.ventas ADD COLUMN checkout_session_id VARCHAR(100);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='payment_intent_id') THEN
    ALTER TABLE public.ventas ADD COLUMN payment_intent_id VARCHAR(100);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='qr_checkout_url') THEN
    ALTER TABLE public.ventas ADD COLUMN qr_checkout_url TEXT;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='currency') THEN
    ALTER TABLE public.ventas ADD COLUMN currency VARCHAR(10) DEFAULT 'USD';
  END IF;

  -- Delivery
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_status') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_status VARCHAR(20);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_address') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_address TEXT;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_lat') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_lat DOUBLE PRECISION;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_lng') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_lng DOUBLE PRECISION;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_distance_km') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_distance_km DOUBLE PRECISION;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_fee') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_fee DOUBLE PRECISION;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_eta_minutes') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_eta_minutes INTEGER;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='ventas' AND column_name='delivery_rider_id') THEN
    ALTER TABLE public.ventas ADD COLUMN delivery_rider_id VARCHAR(50);
  END IF;
END $$;

-- Índices principales
CREATE INDEX IF NOT EXISTS idx_ventas_cliente              ON ventas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_ventas_usuario              ON ventas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha                ON ventas(fecha_venta);
CREATE INDEX IF NOT EXISTS idx_ventas_estado               ON ventas(estado);
-- Índices Payments/Delivery
CREATE INDEX IF NOT EXISTS idx_ventas_payment_intent_id    ON ventas(payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_ventas_checkout_session_id  ON ventas(checkout_session_id);
CREATE INDEX IF NOT EXISTS idx_ventas_delivery_status      ON ventas(delivery_status);

-- ============================================
-- DETALLES DE VENTA
-- ============================================
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_detalle_venta            ON detalle_ventas(venta_id);
CREATE INDEX IF NOT EXISTS idx_detalle_producto         ON detalle_ventas(producto_id);
CREATE INDEX IF NOT EXISTS idx_detalle_venta_producto   ON detalle_ventas(venta_id, producto_id);

-- ============================================
-- TRIGGERS updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS update_categorias_updated_at ON categorias;
CREATE TRIGGER update_categorias_updated_at
  BEFORE UPDATE ON categorias
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_productos_updated_at ON productos;
CREATE TRIGGER update_productos_updated_at
  BEFORE UPDATE ON productos
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_clientes_updated_at ON clientes;
CREATE TRIGGER update_clientes_updated_at
  BEFORE UPDATE ON clientes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_updated_at ON usuarios;
CREATE TRIGGER update_usuarios_updated_at
  BEFORE UPDATE ON usuarios
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEEDS MÍNIMOS (idempotentes)
-- ============================================

-- Categorías
INSERT INTO categorias (nombre, descripcion) VALUES
  ('Electrónica', 'Dispositivos y accesorios electrónicos'),
  ('Ropa',        'Prendas de vestir y accesorios'),
  ('Alimentos',   'Productos comestibles')
ON CONFLICT (nombre) DO NOTHING;

-- Usuario admin (hash de ejemplo; CAMBIAR en prod)
INSERT INTO usuarios (username, password_hash, rol)
VALUES ('admin', '$2a$10$xXxXxXxXxXxXxXxXxXxXx', 'ADMIN')
ON CONFLICT (username) DO NOTHING;

-- Cliente demo
INSERT INTO clientes (nombre, email, telefono)
VALUES ('Cliente Demo', 'demo@example.com', '555-0000')
ON CONFLICT (email) DO NOTHING;

-- Productos iniciales
INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id) VALUES
  ('Laptop HP',      'Laptop 8GB RAM 256GB SSD', 599.99, 10, 1),
  ('Mouse Logitech', 'Mouse inalámbrico',         19.99, 50, 1),
  ('Camiseta Nike',  'Camiseta deportiva',        29.99, 30, 2)
ON CONFLICT DO NOTHING;
