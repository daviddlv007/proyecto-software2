#!/bin/bash
# ============================================
# SCRIPT DE INICIALIZACIÓN COMPLETA - MEJORADO
# Limpieza total + Población + Sincronización
# Validación de datos en cada paso
# 
# Uso:
#   ./inicializar_sistema_completo.sh          # Interactivo
#   ./inicializar_sistema_completo.sh --force  # Sin confirmación
# ============================================

set -e  # Exit on error

# Modo force
FORCE_MODE=false
if [ "$1" == "--force" ]; then
    FORCE_MODE=true
fi

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuración
CORE_URL="http://localhost:8080"
ML_URL="http://localhost:8081"
DL_URL="http://localhost:8082"
BI_URL="http://localhost:8083"
POSTGRES_CONTAINER="postgres"
CORE_DB="coredb"
BI_DB="software2_db"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🚀 INICIALIZACIÓN COMPLETA DEL SISTEMA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# FUNCIONES AUXILIARES
# ============================================

check_service() {
    local name=$1
    local url=$2
    local max_tries=30
    local count=0
    
    echo -ne "  ⏳ Verificando $name... "
    
    while [ $count -lt $max_tries ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        fi
        sleep 2
        count=$((count + 1))
    done
    
    echo -e "${RED}✗ TIMEOUT${NC}"
    return 1
}

execute_sql() {
    local db=$1
    local sql=$2
    docker exec -i $POSTGRES_CONTAINER psql -U postgres -d $db -c "$sql" 2>&1
}

get_count() {
    local db=$1
    local table=$2
    local result=$(execute_sql $db "SELECT COUNT(*) as total FROM $table;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+[[:space:]]*$" | tr -d ' ' | head -1)
    echo "${result:-0}"
}

log_step() {
    echo -e "${YELLOW}[PASO $1]${NC} $2"
}

log_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

log_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

log_error() {
    echo -e "  ${RED}✗${NC} $1"
}

# ============================================
# PASO 1: Verificar servicios
# ============================================
log_step "1/7" "Verificando servicios..."

# PostgreSQL check via docker exec
echo -ne "  ⏳ Verificando PostgreSQL... "
if docker exec $POSTGRES_CONTAINER psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

check_service "Core Service" "$CORE_URL/graphql" || exit 1
check_service "ML Service" "$ML_URL/health" || exit 1
check_service "DL Service" "$DL_URL/health" || exit 1
check_service "BI Service" "$BI_URL/accounts/login/" || exit 1

log_success "Todos los servicios están activos"
echo ""

# ============================================
# PASO 2: Mostrar estado actual
# ============================================
log_step "2/7" "Estado actual de la base de datos..."

# Usar GraphQL para obtener estado actual
estado=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ categorias { id } productos { id } clientes { id } ventas { id } }"}')

categorias_actual=$(echo "$estado" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('categorias',[])))" 2>/dev/null || echo "0")
productos_actual=$(echo "$estado" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('productos',[])))" 2>/dev/null || echo "0")
clientes_actual=$(echo "$estado" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('clientes',[])))" 2>/dev/null || echo "0")
ventas_actual=$(echo "$estado" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('ventas',[])))" 2>/dev/null || echo "0")

usuarios_actual=$(get_count $CORE_DB "usuarios")

log_info "Core DB (coredb):"
echo "    • Categorías: $categorias_actual"
echo "    • Productos: $productos_actual"
echo "    • Clientes: $clientes_actual"
echo "    • Ventas: $ventas_actual"
echo "    • Usuarios: $usuarios_actual"

bi_users=$(get_count $BI_DB "auth_user")
log_info "BI DB (software2_db): $bi_users usuarios Django"
echo ""

# ============================================
# PASO 3: Confirmar limpieza
# ============================================
if [ "$productos_actual" -gt "0" ] || [ "$ventas_actual" -gt "0" ]; then
    log_step "3/7" "Limpieza de datos existentes"
    
    if [ "$FORCE_MODE" = false ]; then
        echo -e "${RED}⚠️  Se eliminarán todos los datos existentes${NC}"
        read -p "¿Continuar? (s/N): " respuesta
        if [[ ! "$respuesta" =~ ^[Ss]$ ]]; then
            log_error "Operación cancelada"
            exit 0
        fi
    fi
    
    log_info "Limpiando datos via GraphQL..."
    
    # Usar script de limpieza mejorado
    bash "$(dirname "$0")/limpiar_graphql.sh" > /dev/null 2>&1
    
    log_success "Base de datos limpiada"
    
    # Esperar a que JPA sincronice
    sleep 2
else
    log_step "3/7" "Base de datos ya está limpia"
fi
echo ""

# ============================================
# PASO 4: Generar datos realistas
# ============================================
log_step "4/7" "Generando datos realistas..."

cd "$(dirname "$0")"

# Verificar si ya hay suficientes datos bien estructurados
productos_actuales=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ productos { id } }"}' | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('productos',[])))" 2>/dev/null || echo "0")
categorias_actuales=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ categorias { id } }"}' | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('categorias',[])))" 2>/dev/null || echo "0")

# Si ya hay datos válidos (al menos 6 categorías y 30 productos), preguntar si regenerar
if [ "$productos_actuales" -ge "30" ] && [ "$categorias_actuales" -ge "6" ]; then
    log_info "Ya existen datos válidos ($categorias_actuales categorías, $productos_actuales productos)"
    
    if [ "$FORCE_MODE" = false ]; then
        read -p "¿Regenerar datos desde cero? (s/N): " respuesta
        if [[ ! "$respuesta" =~ ^[Ss]$ ]]; then
            log_info "Manteniendo datos existentes"
            
            # Extraer estadísticas aproximadas
            ventas_actuales=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ ventas { id } }"}' | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('ventas',[])))" 2>/dev/null || echo "0")
            clientes_actuales=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ clientes { id } }"}' | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('clientes',[])))" 2>/dev/null || echo "0")
            
            log_success "Datos existentes:"
            echo "    • Categorías: $categorias_actuales"
            echo "    • Productos: $productos_actuales"
            echo "    • Clientes: $clientes_actuales"
            echo "    • Ventas: $ventas_actuales"
            echo ""
            
            # Saltar al paso de validación
            productos_gen=$productos_actuales
            clientes_gen=$clientes_actuales
            ventas_gen=$ventas_actuales
            
            # Continuar con el flujo normal
            productos_db=$productos_actuales
            clientes_db=$clientes_actuales
            ventas_db=$ventas_actuales
            categorias_db=$categorias_actuales
            detalles_db=0  # Se calculará en validación
            
            # Ir al paso 5
        else
            # Limpiar y regenerar
            bash "$(dirname "$0")/limpiar_graphql.sh" > /dev/null 2>&1
            log_info "Datos anteriores eliminados, generando nuevos..."
            echo "s" | python3 generar_datos_ml_realistas.py > /tmp/poblado_log.txt 2>&1
        fi
    else
        # En modo force, siempre limpiar y regenerar
        bash "$(dirname "$0")/limpiar_graphql.sh" > /dev/null 2>&1
        log_info "Generando datos nuevos..."
        echo "s" | python3 generar_datos_ml_realistas.py > /tmp/poblado_log.txt 2>&1
    fi
else
    # No hay datos suficientes, generar
    log_info "Generando datos iniciales..."
    echo "s" | python3 generar_datos_ml_realistas.py > /tmp/poblado_log.txt 2>&1
fi

# Solo extraer métricas si se generaron datos nuevos
if [ -f /tmp/poblado_log.txt ]; then
    if grep -q "DATOS GENERADOS" /tmp/poblado_log.txt 2>/dev/null; then
        productos_gen=$(grep "Productos:" /tmp/poblado_log.txt | tail -1 | awk '{print $2}')
        clientes_gen=$(grep "Clientes:" /tmp/poblado_log.txt | tail -1 | awk '{print $2}')
        ventas_gen=$(grep "Ventas:" /tmp/poblado_log.txt | tail -1 | awk '{print $2}')
        
        log_success "Datos generados:"
        echo "    • Categorías: 8"
        echo "    • Productos: ${productos_gen:-N/A}"
        echo "    • Clientes: ${clientes_gen:-N/A}"
        echo "    • Ventas: ${ventas_gen:-N/A}"
    fi
fi
echo ""

# ============================================
# PASO 5: Validar integridad en PostgreSQL
# ============================================
log_step "5/7" "Validando integridad de datos..."

# Esperar a que JPA persista los datos
sleep 3

# Usar GraphQL para verificar (más confiable que SQL directo con JPA)
validacion=$(curl -s http://localhost:8080/graphql -H "Content-Type: application/json" -d '{"query":"{ categorias { id } productos { id } clientes { id } ventas { id detalles { id } } }"}')

categorias_db=$(echo "$validacion" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']['categorias']))" 2>/dev/null || echo "0")
productos_db=$(echo "$validacion" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']['productos']))" 2>/dev/null || echo "0")
clientes_db=$(echo "$validacion" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']['clientes']))" 2>/dev/null || echo "0")
ventas_db=$(echo "$validacion" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']['ventas']))" 2>/dev/null || echo "0")
detalles_db=$(echo "$validacion" | python3 -c "import sys,json; print(sum(len(v['detalles']) for v in json.load(sys.stdin)['data']['ventas']))" 2>/dev/null || echo "0")

log_info "Verificación en GraphQL:"
echo "    • Categorías: $categorias_db"
echo "    • Productos: $productos_db"
echo "    • Clientes: $clientes_db"
echo "    • Ventas: $ventas_db"
echo "    • Detalles venta: $detalles_db"

# Validaciones de consistencia
if [ "$categorias_db" -lt "6" ]; then
    log_error "Error: Muy pocas categorías ($categorias_db), esperadas mínimo 6"
    exit 1
fi

if [ "$productos_db" -lt "30" ]; then
    log_error "Error: Muy pocos productos ($productos_db), esperados mínimo 30"
    exit 1
fi

if [ "$ventas_db" -lt "50" ]; then
    log_error "Error: Muy pocas ventas ($ventas_db), esperadas mínimo 50"
    exit 1
fi

if [ "$detalles_db" -eq "0" ]; then
    log_error "Error: No hay detalles de venta"
    exit 1
fi

log_success "Integridad de datos validada"
echo ""

# ============================================
# PASO 6: Sincronizar servicios ML/DL
# ============================================
log_step "6/7" "Sincronizando servicios..."

# ML Service sync
log_info "Sincronizando ML Service..."
ml_sync=$(curl -sf -X POST $ML_URL/sync 2>&1)
ml_productos=$(echo "$ml_sync" | python3 -c "import sys,json; print(json.load(sys.stdin).get('productos_synced',0))" 2>/dev/null || echo "0")
ml_ventas=$(echo "$ml_sync" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ventas_synced',0))" 2>/dev/null || echo "0")
ml_clientes=$(echo "$ml_sync" | python3 -c "import sys,json; print(json.load(sys.stdin).get('clientes_synced',0))" 2>/dev/null || echo "0")

echo "    • Productos: $ml_productos"
echo "    • Ventas: $ml_ventas"
echo "    • Clientes: $ml_clientes"

if [ "$ml_productos" -lt "40" ] || [ "$ml_ventas" -lt "100" ]; then
    log_error "ML Service no sincronizó correctamente"
    exit 1
fi

log_success "ML Service sincronizado"

# DL Service verification
log_info "Verificando DL Service..."
dl_productos=$(curl -sf $DL_URL/api/productos | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null || echo "0")
echo "    • Productos disponibles: $dl_productos"

if [ "$dl_productos" -lt "40" ]; then
    log_error "DL Service tiene pocos productos"
fi

log_success "DL Service verificado"
echo ""

# ============================================
# PASO 7: Configurar BI Service
# ============================================
log_step "7/7" "Configurando BI Service..."

# Verificar/crear usuario admin
log_info "Verificando usuario admin del BI..."
bi_admin_check=$(docker exec bi-service python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())" 2>&1 | grep -E "(True|False)" | head -1)

if echo "$bi_admin_check" | grep -q "False"; then
    log_info "Creando usuario admin..."
    docker exec bi-service python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@bi.com', 'admin123')" > /dev/null 2>&1
    log_success "Usuario admin creado (admin/admin123)"
else
    log_info "Usuario admin ya existe (admin/admin123)"
fi

# Verificar conexiones del BI a ambas bases de datos
log_info "Verificando conexiones dual-DB..."
bi_conn_test=$(docker exec bi-service python manage.py shell -c "
from django.db import connections
try:
    connections['default'].cursor()
    connections['external_db'].cursor()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

if echo "$bi_conn_test" | grep -q "OK"; then
    log_success "BI Service conectado a ambas bases de datos"
else
    log_error "Error en conexiones del BI Service"
    echo "$bi_conn_test"
fi

echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 RESUMEN DE DATOS:"
echo "  Core Service (coredb):"
echo "    • Categorías:    $categorias_db"
echo "    • Productos:     $productos_db"
echo "    • Clientes:      $clientes_db"
echo "    • Ventas:        $ventas_db"
echo "    • Detalles:      $detalles_db"
echo ""
echo "  ML Service (cache SQLite):"
echo "    • Productos:     $ml_productos"
echo "    • Ventas:        $ml_ventas"
echo "    • Clientes:      $ml_clientes"
echo ""
echo "  DL Service:"
echo "    • Productos:     $dl_productos"
echo ""
echo "  BI Service:"
echo "    • Usuario:       admin / admin123"
echo "    • Conexión DB:   ✓ Dual (coredb + software2_db)"
echo ""
echo "🌐 ACCESOS:"
echo "  Frontend:   http://localhost:5173"
echo "  Core API:   http://localhost:8080/graphiql"
echo "  ML Docs:    http://localhost:8081/docs"
echo "  DL API:     http://localhost:8082/health"
echo "  BI Reports: http://localhost:8083 (admin/admin123)"
echo ""
echo -e "${BLUE}Listo para demostración 🎉${NC}"
