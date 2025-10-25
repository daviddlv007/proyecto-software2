# 🧪 Tests para DL-Service API

Script Python completo para probar toda la API del microservicio de Deep Learning.

## 📋 Requisitos

```bash
pip install requests pillow colorama
```

**Dependencias:**
- `requests`: Cliente HTTP para llamar a la API
- `pillow`: Generación de imágenes de prueba
- `colorama`: Colores en terminal

## 🚀 Uso

### Opción 1: Script Rápido (Bash) ⚡

Prueba rápida de 4 endpoints principales:

```bash
cd dl-service/tests
./quick_test.sh
```

**Incluye:**
- Health check
- Pre-entrenamiento LSTM
- Predicción de ventas
- Recomendaciones

**Tiempo:** ~10 segundos

### Opción 2: Suite Completa (Python) 🧪

Ejecutar todos los tests (19 tests):

```bash
cd dl-service/tests
python test_dl_api.py
```

O directamente:

```bash
python dl-service/tests/test_dl_api.py
```

### Asegurar que el servidor esté corriendo

Antes de ejecutar los tests, asegúrate de que el servidor esté corriendo:

```bash
cd dl-service
npm run dev
```

## 🧪 Tests Incluidos

### **Test 1: Verificar Conexión**
- Verifica que el servidor esté disponible en `http://localhost:8082`
- Hace un ping inicial al endpoint `/health`

### **Test 2: Health Check**
- `GET /health`
- Verifica respuesta con `status: "healthy"`
- Valida estructura de respuesta (service, features)

### **Test 3: Sync - Pre-entrenamiento LSTM**
- `POST /sync`
- Pre-entrena todos los modelos LSTM (productos 1-5)
- Verifica que los 5 modelos se entrenen correctamente
- Mide tiempo de entrenamiento

### **Test 4: Predicción de Ventas (LSTM)**
- `POST /dl/predict-sales/:productId?dias=N`
- Prueba 3 productos diferentes (1, 2, 3)
- Verifica predicciones para 7 y 14 días
- Valida estructura de respuesta (predicciones, estadísticas)
- Muestra total predicho y promedio diario

### **Test 5: Recomendaciones de Productos**
- `GET /dl/recommendations/:productId`
- Prueba todos los productos (1-5)
- Verifica que devuelva lista de recomendaciones
- Muestra productos recomendados

### **Test 6: Clasificación de Imágenes (MobileNet)**
- `POST /dl/classify-image`
- Genera imagen de prueba (224x224 JPEG)
- Envía a MobileNet para clasificación
- Verifica predicciones (top 3)
- Si se mapea a producto: muestra predicción de ventas y recomendaciones
- Mide tiempo de clasificación

### **Test 7: Manejo de Errores**
- Producto inexistente (ID 999)
- Días inválidos (negativos)
- Días excesivos (> 30)
- Verifica códigos de error apropiados (400, 404)

### **Test 8: Performance y Tiempos**
- Mide tiempos de respuesta de endpoints principales
- Hace 3 llamadas a cada endpoint
- Calcula promedio, mínimo y máximo
- Verifica que estén dentro de límites aceptables

## 📊 Salida Esperada

```
╔════════════════════════════════════════════════════════════╗
║           DL-SERVICE API TEST SUITE v1.0                   ║
║          Deep Learning Microservice - Node.js              ║
╚════════════════════════════════════════════════════════════╝

======================================================================
                   TEST 1: VERIFICAR CONEXIÓN
======================================================================

✅ Servicio disponible en http://localhost:8082

======================================================================
                      TEST 2: HEALTH CHECK
======================================================================

ℹ️  Status Code: 200
{
  "status": "healthy",
  "service": "DL Service - Deep Learning REAL",
  "features": [...]
}
✅ Health check OK - Todas las verificaciones pasaron

... (más tests)

======================================================================
                      RESUMEN DE PRUEBAS
======================================================================

Total de pruebas: 25
✅ Exitosas: 25
❌ Fallidas: 0
📊 Tasa de éxito: 100.0%

🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉
```

## 🎨 Características del Script

### **Colores en Terminal**
- ✅ Verde: Tests exitosos
- ❌ Rojo: Tests fallidos
- ⚠️ Amarillo: Advertencias
- ℹ️ Azul: Información

### **Verificaciones Automáticas**
- Validación de estructura JSON
- Verificación de tipos de datos
- Validación de rangos numéricos
- Comprobación de campos requeridos

### **Manejo de Errores**
- Timeout configurable (30s)
- Reintentos automáticos en tests de performance
- Mensajes de error descriptivos
- No falla si Pillow no está instalado (skip test de imagen)

### **Métricas**
- Tiempo de respuesta por endpoint
- Tasa de éxito global
- Contador de tests pasados/fallidos
- Estadísticas de performance

## 🔧 Configuración

Puedes modificar la configuración al inicio del script:

```python
# Configuración
BASE_URL = "http://localhost:8082"  # URL del servidor
TIMEOUT = 30  # Timeout en segundos
```

## 🐛 Troubleshooting

### Error: "No se puede conectar"
```bash
# Asegúrate de que el servidor esté corriendo
cd dl-service
npm run dev
```

### Error: "Module not found"
```bash
# Instala las dependencias
pip install requests colorama pillow
```

### Tests lentos
- Normal en CPU sin GPU
- LSTM puede tardar 1-2 segundos en entrenar
- MobileNet puede tardar 2-5 segundos en primera carga

### Algunos tests fallan
- Verifica que el servidor esté completamente iniciado
- Espera a ver el mensaje "✅ MobileNet cargado"
- Ejecuta `POST /sync` manualmente primero si es necesario

## 📈 Ejemplos de Uso

### Ejecutar solo un test específico
Modifica el método `run_all_tests()` para comentar los tests que no quieras ejecutar.

### Integración con CI/CD
```yaml
# .github/workflows/test.yml
- name: Install Python dependencies
  run: pip install requests colorama pillow

- name: Start DL Service
  run: |
    cd dl-service
    npm install
    npm run dev &
    sleep 10

- name: Run tests
  run: python dl-service/tests/test_dl_api.py
```

## ✅ Checklist de Tests

- [x] Conexión al servidor
- [x] Health check
- [x] Pre-entrenamiento LSTM (sync)
- [x] Predicción de ventas (múltiples productos y días)
- [x] Recomendaciones de productos
- [x] Clasificación de imágenes con MobileNet
- [x] Manejo de errores (IDs inválidos, parámetros incorrectos)
- [x] Performance y tiempos de respuesta

---

**🎉 Script completo y listo para usar**

Prueba toda la funcionalidad del microservicio de Deep Learning de manera automática.
