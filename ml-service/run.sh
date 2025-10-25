#!/bin/bash

# Script de ejecución rápida del ML Service

echo "🚀 Iniciando ML Service..."
echo ""

# Verificar si existe venv
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar venv
source venv/bin/activate

# Instalar/actualizar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Dependencias instaladas"
echo ""
echo "🌐 Iniciando servidor en http://localhost:8081"
echo "📖 Documentación interactiva en http://localhost:8081/docs"
echo ""
echo "⚠️  IMPORTANTE: Asegúrate de que core-service esté corriendo en http://localhost:8080"
echo ""
echo "📝 Primeros pasos:"
echo "   1. Abre http://localhost:8081/docs"
echo "   2. Ejecuta POST /sync para sincronizar datos y entrenar modelos"
echo "   3. Prueba los endpoints de ML"
echo ""

# Ejecutar servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
