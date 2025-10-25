# ============================================
# FRONTEND - Dockerfile Producción
# Vite Preview Server (2025 - Más eficiente que nginx para SPAs)
# Moderno, minimalista y optimizado
# ============================================

FROM node:20-alpine AS builder

WORKDIR /build

# Copiar package files para cache
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# ============================================
# STAGE: Vite Preview Server (Moderno 2025)
# Más eficiente que nginx para SPAs React
# ============================================
FROM node:20-alpine

# Metadata
LABEL maintainer="proyecto-sw2"
LABEL service="frontend"
LABEL description="React Frontend SPA - Vite Preview"

WORKDIR /app

# Solo necesitamos package.json y los archivos built
COPY package*.json ./
COPY --from=builder /build/dist ./dist

# Instalar solo dependencias de producción necesarias para preview
RUN npm ci --only=production

# Instalar wget para healthcheck
RUN apk add --no-cache wget

# Exponer puerto de Vite Preview
EXPOSE 4173

# Health check usando wget (más confiable que nc en BusyBox Alpine)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider --timeout=3 http://localhost:4173/ || exit 1

# Vite preview server (más eficiente que nginx para SPAs)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
