-- ============================================
-- POSTGRESQL - Inicialización de Bases de Datos
-- Se ejecuta automáticamente al primer arranque
-- ============================================

-- Base de datos principal del core service (ya existe)
-- CREATE DATABASE coredb;

-- Base de datos para el BI service (Django)
CREATE DATABASE "software2_DB";

-- Configuraciones opcionales para el BI service
\c "software2_DB";

-- Extensiones útiles para BI/Analytics
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Usuario específico para BI (opcional - usa postgres por simplicidad)
-- CREATE USER bi_user WITH PASSWORD 'bi_password';
-- GRANT ALL PRIVILEGES ON DATABASE "software2_DB" TO bi_user;

-- Log de inicialización
\echo 'Database software2_DB created successfully for BI service';