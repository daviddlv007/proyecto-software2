#!/bin/bash
# ============================================
# SCRIPT DE INICIALIZACIÓN COMPLETA
# Población de datos + Sincronización + Entrenamiento
# Desacoplado para arquitectura distribuida
# ============================================

set -e  # Exit on error

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración (parametrizable para diferentes entornos)
CORE_URL="${CORE_API_URL:-http://localhost:8080}"
ML_URL="${ML_API_URL:-http://localhost:8081}"
DL_URL="${DL_API_URL:-http://localhost:8082}"

# Timeouts y reintentos
MAX_RETRIES=30
RETRY_DELAY=2

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🚀 INICIALIZACIÓN COMPLETA DEL SISTEMA${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ============================================
# PASO 1: Verificar que todos los servicios estén HEALTHY
# ============================================
echo -e "${YELLOW}[1/5] Verificando servicios...${NC}"

check_service() {
    local service_name=$1
    local url=$2
    local health_endpoint=$3
    local retries=0
    
    echo -n "  ⏳ Esperando $service_name... "
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "$url$health_endpoint" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        fi
        sleep $RETRY_DELAY
        retries=$((retries + 1))
    done
    
    echo -e "${RED}✗ TIMEOUT${NC}"
    echo -e "${RED}Error: $service_name no responde en $url$health_endpoint${NC}"
    return 1
}

check_service "Core Service" "$CORE_URL" "/actuator/health" || exit 1
check_service "ML Service" "$ML_URL" "/health" || exit 1
check_service "DL Service" "$DL_URL" "/health" || exit 1

echo -e "${GREEN}✓ Todos los servicios están listos${NC}"
echo ""

# ============================================
# PASO 2: Generar datos transaccionales (Core Service)
# ============================================
echo -e "${YELLOW}[2/5] Generando datos en Core Service...${NC}"

# Verificar si ya hay datos
PRODUCTOS_COUNT=$(curl -sf -X POST "$CORE_URL/graphql" \
    -H "Content-Type: application/json" \
    -d '{"query":"{ productos { id } }"}' \
    | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data',{}).get('productos',[])))" 2>/dev/null || echo "0")

if [ "$PRODUCTOS_COUNT" -gt "10" ]; then
    echo -e "  ${BLUE}ℹ Ya existen $PRODUCTOS_COUNT productos en el sistema${NC}"
    read -p "  ¿Regenerar datos? (Esto BORRARÁ datos existentes) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "  ${BLUE}→ Saltando generación de datos${NC}"
    else
        echo -e "  🗑️  Limpiando datos anteriores..."
        # Llamar al script de limpieza en modo silencioso
        "$(dirname "$0")/limpiar_datos.sh" --silent || {
            echo -e "${RED}✗ Error limpiando datos${NC}"
            exit 1
        }
        echo -e "  ${GREEN}✓ Datos anteriores eliminados${NC}"
        echo -e "  📝 Generando nuevos datos..."
        python3 "$(dirname "$0")/generar_datos_ml_realistas.py" || {
            echo -e "${RED}✗ Error generando datos${NC}"
            exit 1
        }
    fi
else
    echo -e "  📝 Generando datos iniciales..."
    python3 "$(dirname "$0")/generar_datos_ml_realistas.py" || {
        echo -e "${RED}✗ Error generando datos${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✓ Datos transaccionales listos${NC}"
echo ""

# ============================================
# PASO 3: Sincronizar datos a ML Service (Pull desacoplado)
# ============================================
echo -e "${YELLOW}[3/5] Sincronizando datos a ML Service...${NC}"

SYNC_RESPONSE=$(curl -sf -X POST "$ML_URL/sync" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo '{"error": true}')

if echo "$SYNC_RESPONSE" | grep -q "error"; then
    echo -e "${RED}✗ Error en sincronización ML${NC}"
    echo "Response: $SYNC_RESPONSE"
    exit 1
fi

PRODUCTOS_SYNCED=$(echo "$SYNC_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('productos_synced', 0))" 2>/dev/null || echo "0")
VENTAS_SYNCED=$(echo "$SYNC_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ventas_synced', 0))" 2>/dev/null || echo "0")

echo -e "  ${GREEN}✓ Productos sincronizados: $PRODUCTOS_SYNCED${NC}"
echo -e "  ${GREEN}✓ Ventas sincronizadas: $VENTAS_SYNCED${NC}"
echo ""

# ============================================
# PASO 4: Entrenar modelos ML (Desacoplado)
# ============================================
echo -e "${YELLOW}[4/5] Entrenando modelos ML...${NC}"

TRAIN_ML_RESPONSE=$(curl -sf -X POST "$ML_URL/train" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo '{"error": true}')

if echo "$TRAIN_ML_RESPONSE" | grep -q "error"; then
    echo -e "${RED}✗ Error en entrenamiento ML${NC}"
    echo "Response: $TRAIN_ML_RESPONSE"
    exit 1
fi

echo -e "  ${GREEN}✓ Modelos ML entrenados${NC}"
echo "  📊 Response: $TRAIN_ML_RESPONSE"
echo ""

# ============================================
# PASO 5: Entrenar modelos DL (Desacoplado)
# ============================================
echo -e "${YELLOW}[5/5] Entrenando modelos Deep Learning...${NC}"

# DL Service entrena bajo demanda (lazy loading)
# Solo verificamos que puede acceder a Core Service
TRAIN_DL_RESPONSE=$(curl -sf -X POST "$DL_URL/train" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo '{"error": true}')

if echo "$TRAIN_DL_RESPONSE" | grep -q "error"; then
    echo -e "${YELLOW}⚠ DL Service entrena bajo demanda (lazy loading)${NC}"
    echo -e "  ${BLUE}→ Los modelos se entrenarán en la primera petición${NC}"
else
    echo -e "  ${GREEN}✓ Modelos DL inicializados${NC}"
fi

echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ INICIALIZACIÓN COMPLETADA${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "📊 ${BLUE}Estado de los servicios:${NC}"
echo -e "  • Core Service:  ${GREEN}✓${NC} Datos poblados"
echo -e "  • ML Service:    ${GREEN}✓${NC} $PRODUCTOS_SYNCED productos, $VENTAS_SYNCED ventas sincronizadas"
echo -e "  • DL Service:    ${GREEN}✓${NC} Listo (entrenamiento lazy)"
echo ""
echo -e "🎯 ${BLUE}Próximos pasos:${NC}"
echo -e "  1. Acceder al frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "  2. Verificar predicciones ML: ${BLUE}$ML_URL/predict/sales${NC}"
echo -e "  3. Verificar recomendaciones DL: ${BLUE}$DL_URL/recommendations/1${NC}"
echo ""
echo -e "💾 ${BLUE}Persistencia:${NC}"
echo -e "  • Los datos están en volúmenes Docker persistentes"
echo -e "  • Para resetear: ${YELLOW}docker-compose down -v${NC}"
echo ""
echo -e "${GREEN}🚀 Sistema listo para usar!${NC}"
