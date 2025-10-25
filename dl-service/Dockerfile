# ============================================
# DL SERVICE - Dockerfile Multi-Stage
# Node.js + TensorFlow.js + PostgreSQL
# Optimizado para bajo consumo de recursos
# ============================================

# ============================================
# STAGE 1: Build TypeScript
# ============================================
FROM node:20-alpine AS builder

WORKDIR /build

# Copiar package files para aprovechar cache
COPY package*.json ./
COPY tsconfig.json ./

# Instalar todas las dependencias (incluidas dev)
RUN npm ci

# Copiar código fuente
COPY src ./src

# Compilar TypeScript
RUN npm run build

# ============================================
# STAGE 2: Runtime (imagen mínima)
# ============================================
FROM node:20-alpine

# Metadata
LABEL maintainer="proyecto-sw2"
LABEL service="dl-service"
LABEL description="Deep Learning API Service with TensorFlow.js"

# Variables de entorno por defecto
ENV NODE_ENV=production \
    PORT=8082 \
    NODE_OPTIONS="--max-old-space-size=512" \
    DATABASE_URL="" \
    CORE_SERVICE_URL=http://core-service:8080/graphql

# Instalar dependencias del sistema para TensorFlow.js y canvas
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    giflib-dev \
    pixman-dev

# Crear usuario no-root
RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar solo dependencias de producción
RUN npm ci --only=production && npm cache clean --force

# Copiar código compilado desde builder
COPY --from=builder /build/dist ./dist

# Copiar otros archivos necesarios
COPY db ./db

# Crear directorios necesarios
RUN mkdir -p data uploads models && \
    chown -R appuser:appgroup /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8082

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8082/health || exit 1

# Comando de inicio
CMD ["node", "dist/server-production.js"]
