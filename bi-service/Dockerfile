# ============================================
# BI SERVICE - Dockerfile Multi-Stage
# Django + PostgreSQL + Google Generative AI
# ============================================

FROM python:3.12-slim AS base

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ============================================
# STAGE 1: Dependencies
# ============================================
FROM base AS dependencies

# Instalar dependencias del sistema para PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# STAGE 2: Runtime
# ============================================
FROM base AS runtime

# Instalar solo librerías runtime de PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p static media

# Exponer puerto
EXPOSE 8083

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8083', timeout=5)" || exit 1

# Comando de inicio
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python auto_connect_coredb.py && python manage.py runserver 0.0.0.0:8083"]
