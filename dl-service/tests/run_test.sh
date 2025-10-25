#!/bin/bash

# Script para ejecutar el test completo de la API de DL Service

echo "🧪 Ejecutando tests completos de DL Service API..."
echo ""

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

# Verificar e instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
python3 -c "import requests" 2>/dev/null || pip install requests
python3 -c "import PIL" 2>/dev/null || pip install pillow
python3 -c "import colorama" 2>/dev/null || pip install colorama

echo ""

# Ejecutar tests
python3 "$(dirname "$0")/test_api_completo.py"

exit $?
