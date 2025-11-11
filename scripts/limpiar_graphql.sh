#!/bin/bash
# ============================================
# LIMPIEZA COMPLETA DE DATOS - MEJORADO
# Usa GraphQL mutations para eliminar correctamente
# ============================================

set -e

CORE_URL="http://localhost:8080/graphql"

echo "🧹 Limpiando datos via GraphQL..."

# Función para obtener IDs
get_ids() {
    local query=$1
    curl -s -X POST "$CORE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"$query\"}" \
        | python3 -c "import sys,json; data=json.load(sys.stdin); print(' '.join([str(item['id']) for item in data['data']['${2}']]))" 2>/dev/null || echo ""
}

# Función para eliminar
delete_item() {
    local mutation=$1
    curl -s -X POST "$CORE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"$mutation\"}" > /dev/null 2>&1
}

# 1. Eliminar ventas (esto también elimina detalles por CASCADE)
echo "  Eliminando ventas..."
ventas_ids=$(get_ids "query { ventas { id } }" "ventas")
count=0
for id in $ventas_ids; do
    delete_item "mutation { deleteVenta(id: $id) }"
    count=$((count + 1))
done
echo "    ✓ $count ventas eliminadas"

# 2. Eliminar productos
echo "  Eliminando productos..."
productos_ids=$(get_ids "query { productos { id } }" "productos")
count=0
for id in $productos_ids; do
    delete_item "mutation { deleteProducto(id: $id) }"
    count=$((count + 1))
done
echo "    ✓ $count productos eliminados"

# 3. Eliminar clientes
echo "  Eliminando clientes..."
clientes_ids=$(get_ids "query { clientes { id } }" "clientes")
count=0
for id in $clientes_ids; do
    delete_item "mutation { deleteCliente(id: $id) }"
    count=$((count + 1))
done
echo "    ✓ $count clientes eliminados"

# 4. Eliminar categorías
echo "  Eliminando categorías..."
categorias_ids=$(get_ids "query { categorias { id } }" "categorias")
count=0
for id in $categorias_ids; do
    delete_item "mutation { deleteCategoria(id: $id) }"
    count=$((count + 1))
done
echo "    ✓ $count categorías eliminadas"

echo "✅ Limpieza completada"
