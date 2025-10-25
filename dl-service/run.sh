#!/bin/bash

# Script de inicio para DL Service
echo "🚀 Iniciando DL Service..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creando archivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    echo "Por favor instala Node.js >= 18.0.0"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
fi

# Crear directorios necesarios
mkdir -p data uploads models

# Iniciar servidor en modo desarrollo
echo -e "${GREEN}🚀 Iniciando servidor en modo desarrollo...${NC}"
echo ""
npm run dev
