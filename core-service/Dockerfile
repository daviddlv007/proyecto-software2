# ============================================
# CORE SERVICE - Dockerfile Multi-Stage
# Spring Boot + PostgreSQL
# Optimizado para bajo consumo de recursos
# ============================================

# ============================================
# STAGE 1: Build
# ============================================
FROM maven:3.9-eclipse-temurin-17-alpine AS builder

WORKDIR /build

# Copiar solo pom.xml primero para aprovechar cache de Docker
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copiar código fuente y compilar
COPY src ./src
RUN mvn clean package -DskipTests -B

# ============================================
# STAGE 2: Runtime (imagen mínima)
# ============================================
FROM eclipse-temurin:17-jre-alpine

# Metadata
LABEL maintainer="proyecto-sw2"
LABEL service="core-service"
LABEL description="Core GraphQL API Service"

# Variables de entorno por defecto (sobreescribibles)
ENV SPRING_PROFILES_ACTIVE=production \
    SERVER_PORT=8080 \
    JAVA_OPTS="-Xms128m -Xmx512m -XX:+UseG1GC -XX:MaxGCPauseMillis=200" \
    DATABASE_URL="" \
    DATABASE_USERNAME=core_user \
    DATABASE_PASSWORD=""

# Crear usuario no-root para seguridad
RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

WORKDIR /app

# Copiar JAR desde stage de build
COPY --from=builder /build/target/*.jar app.jar

# Crear directorio de datos y dar permisos
RUN mkdir -p /data && \
    chown -R appuser:appgroup /app /data

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Comando de inicio con JVM optimizada para recursos limitados
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
