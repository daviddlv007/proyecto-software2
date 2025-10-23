#!/bin/bash

# Script para ejecutar los tests con pytest
# Uso: ./run_tests.sh [opciones]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Suite de Tests GraphQL - Pytest + GQL         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado. Creando...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar si las dependencias están instaladas
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencias no instaladas. Instalando...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencias instaladas${NC}"
fi

echo -e "${BLUE}🚀 Ejecutando tests...${NC}"
echo

# Ejecutar pytest con las opciones proporcionadas o las predeterminadas
if [ $# -eq 0 ]; then
    # Sin argumentos: ejecutar con reporte HTML
    pytest -v --html=report.html --self-contained-html
else
    # Con argumentos: pasar todos los argumentos a pytest
    pytest "$@"
fi

EXIT_CODE=$?

echo
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            ✓ TODOS LOS TESTS PASARON            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    
    if [ -f "report.html" ]; then
        echo -e "${BLUE}📊 Reporte HTML generado: report.html${NC}"
        echo -e "${BLUE}   Ábrelo con: firefox report.html${NC}"
    fi
else
    echo -e "${RED}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            ✗ ALGUNOS TESTS FALLARON             ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════╝${NC}"
fi

echo
echo -e "${YELLOW}💡 Comandos útiles:${NC}"
echo -e "   ${BLUE}./run_tests.sh${NC}                    - Ejecutar todos los tests"
echo -e "   ${BLUE}./run_tests.sh -m smoke${NC}          - Solo tests smoke (rápidos)"
echo -e "   ${BLUE}./run_tests.sh test_ventas.py${NC}    - Solo tests de ventas"
echo -e "   ${BLUE}./run_tests.sh -k crear${NC}          - Tests que contengan 'crear'"
echo -e "   ${BLUE}./run_tests.sh -v -s${NC}             - Verbose + mostrar prints"
echo -e "   ${BLUE}./run_tests.sh --cov${NC}             - Con cobertura de código"

exit $EXIT_CODE
