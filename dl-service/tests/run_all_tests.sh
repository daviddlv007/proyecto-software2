#!/usr/bin/env bash
# Unified test runner for DL Service

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🧪 DL Service - Run all tests"

# Ensure python3 available
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 no encontrado"
  exit 1
fi

# Install minimal deps if missing
python3 - <<'PY'
import sys
import importlib
reqs = ['requests','PIL','colorama']
for r in reqs:
    name = r if r!='PIL' else 'PIL'
    try:
        importlib.import_module('PIL') if r=='PIL' else importlib.import_module(r)
    except Exception:
        print(f"Instalando dependencia: {r}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', r])
print('Dependencias instaladas o ya presentes')
PY

echo ""
echo "Ejecutando tests: test_api_completo.py"
python3 "$ROOT_DIR/test_api_completo.py"

echo "\n✅ Test runner finalizado"
