# ============================================
# ML SERVICE - Dockerfile Multi-Stage
# FastAPI + PostgreSQL + Scikit-learn
# Optimizado para bajo consumo de recursos
# ============================================

# ============================================
# STAGE 1: Build dependencies
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar en virtual env
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================
# STAGE 2: Runtime (imagen mínima)
# ============================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="proyecto-sw2"
LABEL service="ml-service"
LABEL description="Machine Learning API Service"

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8081 \
    DATABASE_URL="" \
    CORE_SERVICE_URL=http://core-service:8080/graphql \
    WORKERS=1

# Instalar solo runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar virtual env desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY app ./app
COPY db ./db

# Crear directorios para modelos y datos
RUN mkdir -p /app/models /data && \
    chown -R appuser:appuser /app /data

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8081/health', timeout=5)" || exit 1

# Comando de inicio (con 1 worker para bajo consumo)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "1"]
