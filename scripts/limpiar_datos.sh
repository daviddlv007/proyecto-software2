#!/bin/bash

# ================================================
# Script de Limpieza de Datos
# Elimina todas las ventas, clientes y productos
# Mantiene categorías y estructura base
# 
# Uso:
#   ./limpiar_datos.sh           # Modo interactivo
#   ./limpiar_datos.sh --silent  # Sin confirmación (para scripts)
# ================================================

set -e  # Detener en caso de error

CORE_URL="http://localhost:8080/graphql"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Modo silencioso si se pasa --silent
SILENT_MODE=false
if [ "$1" == "--silent" ]; then
    SILENT_MODE=true
fi

if [ "$SILENT_MODE" = false ]; then
    echo -e "${YELLOW}╔══════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  🧹 LIMPIEZA DE BASE DE DATOS          ║${NC}"
    echo -e "${YELLOW}╔══════════════════════════════════════════╗${NC}"
    echo ""
fi

# Verificar que el Core Service esté activo
if [ "$SILENT_MODE" = false ]; then
    echo "📡 Verificando conexión con Core Service..."
fi

if ! curl -s -o /dev/null -w "%{http_code}" "$CORE_URL" | grep -q "200\|400"; then
    echo -e "${RED}❌ Error: Core Service no está disponible en $CORE_URL${NC}"
    exit 1
fi

if [ "$SILENT_MODE" = false ]; then
    echo -e "${GREEN}✅ Core Service conectado${NC}"
    echo ""
fi

# Función para ejecutar mutation GraphQL
execute_mutation() {
    local query="$1"
    local description="$2"
    
    if [ "$SILENT_MODE" = false ]; then
        echo -ne "🔄 $description... "
    fi
    
    response=$(curl -s -X POST "$CORE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"$query\"}")
    
    if echo "$response" | grep -q '"errors"'; then
        if [ "$SILENT_MODE" = false ]; then
            echo -e "${RED}❌ Error${NC}"
            echo "$response" | jq '.'
        fi
        return 1
    else
        if [ "$SILENT_MODE" = false ]; then
            echo -e "${GREEN}✅ Completado${NC}"
        fi
        return 0
    fi
}

# Contar registros actuales
if [ "$SILENT_MODE" = false ]; then
    echo "📊 Contando registros actuales..."
fi

count_query='query { productos { id } clientes { id } ventas { id } }'
count_response=$(curl -s -X POST "$CORE_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$count_query\"}")

productos_count=$(echo "$count_response" | jq '.data.productos | length')
clientes_count=$(echo "$count_response" | jq '.data.clientes | length')
ventas_count=$(echo "$count_response" | jq '.data.ventas | length')

if [ "$SILENT_MODE" = false ]; then
    echo -e "  • Productos: ${YELLOW}$productos_count${NC}"
    echo -e "  • Clientes: ${YELLOW}$clientes_count${NC}"
    echo -e "  • Ventas: ${YELLOW}$ventas_count${NC}"
    echo ""

    # Confirmar con el usuario
    echo -e "${RED}⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos${NC}"
    read -p "¿Desea continuar? (escriba 'SI' para confirmar): " confirm

    if [ "$confirm" != "SI" ]; then
        echo -e "${YELLOW}❌ Operación cancelada${NC}"
        exit 0
    fi

    echo ""
    echo "🗑️  Iniciando limpieza..."
    echo ""
fi

# 1. Obtener y eliminar todas las ventas
if [ "$SILENT_MODE" = false ]; then
    echo "1️⃣  Eliminando ventas..."
fi

ventas_query='query { ventas { id } }'
ventas_response=$(curl -s -X POST "$CORE_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$ventas_query\"}")

ventas_ids=$(echo "$ventas_response" | jq -r '.data.ventas[].id')

if [ -n "$ventas_ids" ]; then
    for id in $ventas_ids; do
        delete_mutation="mutation { deleteVenta(id: $id) }"
        execute_mutation "$delete_mutation" "   Eliminando venta #$id"
    done
else
    if [ "$SILENT_MODE" = false ]; then
        echo -e "   ${YELLOW}ℹ️  No hay ventas para eliminar${NC}"
    fi
fi

if [ "$SILENT_MODE" = false ]; then
    echo ""
fi

# 2. Obtener y eliminar todos los clientes
if [ "$SILENT_MODE" = false ]; then
    echo "2️⃣  Eliminando clientes..."
fi

clientes_query='query { clientes { id } }'
clientes_response=$(curl -s -X POST "$CORE_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$clientes_query\"}")

clientes_ids=$(echo "$clientes_response" | jq -r '.data.clientes[].id')

if [ -n "$clientes_ids" ]; then
    for id in $clientes_ids; do
        delete_mutation="mutation { deleteCliente(id: $id) }"
        execute_mutation "$delete_mutation" "   Eliminando cliente #$id"
    done
else
    if [ "$SILENT_MODE" = false ]; then
        echo -e "   ${YELLOW}ℹ️  No hay clientes para eliminar${NC}"
    fi
fi

if [ "$SILENT_MODE" = false ]; then
    echo ""
fi

# 3. Obtener y eliminar todos los productos
if [ "$SILENT_MODE" = false ]; then
    echo "3️⃣  Eliminando productos..."
fi

productos_query='query { productos { id } }'
productos_response=$(curl -s -X POST "$CORE_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$productos_query\"}")

productos_ids=$(echo "$productos_response" | jq -r '.data.productos[].id')

if [ -n "$productos_ids" ]; then
    for id in $productos_ids; do
        delete_mutation="mutation { deleteProducto(id: $id) }"
        execute_mutation "$delete_mutation" "   Eliminando producto #$id"
    done
else
    if [ "$SILENT_MODE" = false ]; then
        echo -e "   ${YELLOW}ℹ️  No hay productos para eliminar${NC}"
    fi
fi

if [ "$SILENT_MODE" = false ]; then
    echo ""
    
    # Verificar estado final
    echo "📊 Verificando estado final..."
    final_response=$(curl -s -X POST "$CORE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"$count_query\"}")

    final_productos=$(echo "$final_response" | jq '.data.productos | length')
    final_clientes=$(echo "$final_response" | jq '.data.clientes | length')
    final_ventas=$(echo "$final_response" | jq '.data.ventas | length')

    echo -e "  • Productos: ${GREEN}$final_productos${NC}"
    echo -e "  • Clientes: ${GREEN}$final_clientes${NC}"
    echo -e "  • Ventas: ${GREEN}$final_ventas${NC}"
    echo ""

    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ LIMPIEZA COMPLETADA                 ║${NC}"
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo ""
    echo "💡 Para volver a poblar la base de datos, ejecuta:"
    echo "   cd scripts && python3 generar_datos_ml_realistas.py"
    echo ""
fi
