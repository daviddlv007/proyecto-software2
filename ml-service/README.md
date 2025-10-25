# 🤖 ML Service - Microservicio de Machine Learning

Microservicio de Machine Learning para análisis predictivo del sistema de gestión de supermercado.

## 🎯 Características

### ✅ Arquitectura Moderna
- **Framework:** FastAPI (Python) - El más rápido y moderno para APIs REST
- **ML:** scikit-learn - Modelos pre-entrenados, sin GPUs, implementación inmediata
- **Base de Datos:** SQLite embebido - Caché local, no requiere instalación
- **Documentación:** Swagger/OpenAPI automática en `/docs`

### ✅ 3 Tipos de ML Implementados

#### 1. **Supervisado** - Predicción de Precios
- **Algoritmo:** Regresión Lineal
- **Features:** Categoría, Stock, Longitud del nombre
- **Uso:** Sugerir precio para nuevos productos
- **Endpoint:** `POST /predict/price`

#### 2. **No Supervisado** - Segmentación de Clientes
- **Algoritmo:** K-Means (3 clusters)
- **Features:** Total compras, Frecuencia, Ticket promedio
- **Uso:** Identificar clientes VIP/Regular/Ocasional
- **Endpoint:** `GET /ml/segmentacion`

#### 3. **Semi-Supervisado** - Detección de Anomalías
- **Algoritmo:** Isolation Forest
- **Features:** Total venta, Número de productos, Ticket promedio
- **Uso:** Detectar posibles fraudes o errores
- **Endpoint:** `GET /ml/anomalias`

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- core-service corriendo en `http://localhost:8080`
- Datos poblados en core-service (ejecutar script de generación)

### Instalación y Ejecución

```bash
cd ml-service
./run.sh
```

El script automáticamente:
1. ✅ Crea entorno virtual
2. ✅ Instala dependencias
3. ✅ Inicia servidor en puerto 8081
4. ✅ Abre documentación en http://localhost:8081/docs

### Ejecución Manual

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

## 📖 Uso de la API

### 1. Sincronización Inicial (Obligatorio)

**Endpoint:** `POST /sync`

Sincroniza datos desde core-service y entrena los 3 modelos.

```bash
curl -X POST http://localhost:8081/sync
```

**Response:**
```json
{
  "productos_synced": 50,
  "ventas_synced": 280,
  "clientes_synced": 25,
  "timestamp": "2025-10-24T10:30:00"
}
```

### 2. Predicción de Precios

**Endpoint:** `POST /predict/price`

```bash
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "Bebidas",
    "stock": 50,
    "nombre": "Jugo de Mango 1L"
  }'
```

**Response:**
```json
{
  "precio_sugerido": 3.15,
  "categoria": "Bebidas",
  "confianza": 0.85,
  "features_used": ["categoria", "stock", "longitud_nombre"]
}
```

### 3. Segmentación de Clientes

**Endpoint:** `GET /ml/segmentacion`

```bash
curl http://localhost:8081/ml/segmentacion
```

**Response:**
```json
{
  "total_clientes": 25,
  "vip_count": 5,
  "regular_count": 12,
  "ocasional_count": 8,
  "clientes": [
    {
      "cliente_id": 1,
      "nombre": "María González",
      "segmento": "VIP",
      "total_compras": 450.50,
      "frecuencia": 15,
      "ticket_promedio": 30.03
    },
    ...
  ]
}
```

### 4. Detección de Anomalías

**Endpoint:** `GET /ml/anomalias`

```bash
curl http://localhost:8081/ml/anomalias
```

**Response:**
```json
{
  "total_ventas_analizadas": 280,
  "anomalias_detectadas": 12,
  "anomalias": [
    {
      "venta_id": 45,
      "fecha": "2025-10-15",
      "total": 150.00,
      "score_anomalia": -0.35,
      "razon": "Total muy alto | Muchos productos"
    },
    ...
  ]
}
```

### 5. Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8081/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ml-service",
  "core_service_reachable": true,
  "models_trained": true,
  "cache_size": {
    "productos": 50,
    "ventas": 280,
    "clientes": 25
  }
}
```

## 🏗️ Arquitectura

```
┌─────────────────┐       GraphQL        ┌──────────────────┐
│  core-service   │◄─────────────────────│   ml-service     │
│  (Puerto 8080)  │                      │  (Puerto 8081)   │
│  Spring Boot    │                      │    FastAPI       │
│  GraphQL        │                      │    REST API      │
│  H2 Database    │                      │    SQLite Cache  │
└────────┬────────┘                      └────────┬─────────┘
         │                                        │
         │                                        │
         │             REST API                   │
         │        ┌─────────────────┐            │
         └────────►│   Frontend      │◄───────────┘
                  │  (Puerto 5173)  │
                  │   React + TS    │
                  └─────────────────┘
```

### Flujo de Datos

1. **Sincronización:** ml-service consulta core-service via GraphQL
2. **Caché:** Datos se almacenan en SQLite local
3. **Entrenamiento:** Los 3 modelos se entrenan automáticamente
4. **Predicción:** Frontend consulta ml-service via REST
5. **Actualización:** Re-sincronizar periódicamente para nuevos datos

## 📂 Estructura del Proyecto

```
ml-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + endpoints
│   ├── database.py          # SQLite models y conexión
│   ├── schemas.py           # Pydantic schemas (request/response)
│   └── services/
│       ├── __init__.py
│       ├── data_sync.py     # Sincronización con core-service
│       ├── predictor.py     # ML Supervisado (precios)
│       ├── segmentacion.py  # ML No Supervisado (clustering)
│       └── anomalias.py     # ML Semi-Supervisado (anomalías)
├── requirements.txt         # Dependencias Python
├── run.sh                   # Script de ejecución rápida
└── README.md               # Esta documentación
```

## 🗄️ Base de Datos (SQLite)

### Tablas

#### `productos_cache`
```sql
id, nombre, categoria, precio, stock, synced_at
```

#### `ventas_cache`
```sql
id, cliente_id, fecha, total, num_productos, synced_at
```

#### `cliente_metrics`
```sql
id, cliente_id, nombre, total_compras, frecuencia, 
ticket_promedio, segmento, updated_at
```

#### `model_metadata`
```sql
id, model_name, trained_at, accuracy, samples_count, features
```

**Ubicación:** `ml-service/ml_cache.db` (se crea automáticamente)

## 🔧 Configuración

### Variables de Entorno (opcional)

Crear `.env` en la raíz de `ml-service/`:

```env
# URL del core-service
CORE_SERVICE_URL=http://localhost:8080/graphql

# Puerto del ml-service
ML_SERVICE_PORT=8081

# Nivel de logging
LOG_LEVEL=INFO
```

## 🧪 Testing

### Script Automatizado (Recomendado)

El microservicio incluye un script completo de testing que prueba **toda la API** automáticamente:

```bash
# Desde la raíz del proyecto
cd ml-service
python3 tests/test_ml_service.py
```

**El script prueba:**
- ✅ Conectividad con core-service (puerto 8080)
- ✅ Health check del ML service (puerto 8081)
- ✅ Sincronización de datos desde core-service
- ✅ Predicción de precios (ML Supervisado)
- ✅ Segmentación de clientes (ML No Supervisado)
- ✅ Detección de anomalías (ML Semi-Supervisado)
- ✅ Metadata de modelos
- ✅ Endpoint raíz (info del servicio)

**Output esperado:**
```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           TEST COMPLETO DEL MICROSERVICIO ML                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

ℹ Fecha: 2025-10-24 11:30:00
ℹ ML Service URL: http://localhost:8081
ℹ Core Service URL: http://localhost:8080

======================================================================
                1. VERIFICACIÓN DE CORE SERVICE
======================================================================

✓ Conectividad con core-service
  GraphQL endpoint respondiendo en puerto 8080

... [más tests] ...

======================================================================
                        RESUMEN DE TESTS
======================================================================

Tests ejecutados: 20
Tests exitosos: 20
Tests fallidos: 0
Tasa de éxito: 100.0%
Tiempo total: 12.45 segundos

✓ TODOS LOS TESTS PASARON ✓
El microservicio ML está funcionando correctamente
```

### Requisitos para Testing

1. **core-service** debe estar corriendo en puerto 8080
2. **ml-service** debe estar corriendo en puerto 8081
3. Base de datos poblada con datos (ejecutar `scripts/generar_datos_ml_realistas.py`)

### Probar con cURL

```bash
# Health check
curl http://localhost:8081/health

# Sincronizar
curl -X POST http://localhost:8081/sync

# Predecir precio
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{"categoria": "Lácteos", "stock": 100, "nombre": "Yogurt Natural"}'

# Ver segmentación
curl http://localhost:8081/ml/segmentacion

# Ver anomalías
curl http://localhost:8081/ml/anomalias
```

### Probar con Swagger UI

Abrir http://localhost:8081/docs y probar interactivamente todos los endpoints.

## 📊 Casos de Uso

### 1. Sugerir Precio para Nuevo Producto
```
Usuario → Frontend → POST /predict/price → ML Service → Precio Sugerido
```

### 2. Identificar Clientes VIP
```
Usuario → Frontend → GET /ml/segmentacion → ML Service → Lista de Clientes VIP
```

### 3. Alertar Ventas Sospechosas
```
Sistema → GET /ml/anomalias → ML Service → Alertas de Anomalías
```

### 4. Dashboard de Analytics
```
Frontend → GET /ml/segmentacion + /ml/anomalias → Visualizar en Gráficas
```

## 🎓 Ventajas de esta Arquitectura

### ✅ Simplicidad
- FastAPI: Framework más simple y rápido
- sklearn: Sin GPUs, sin TensorFlow, sin complejidad
- SQLite: No requiere instalación de BD

### ✅ Rapidez
- Modelos ligeros: Entrenan en < 1 segundo
- Predicciones instantáneas: < 10ms
- Sin overhead de frameworks pesados

### ✅ Escalabilidad
- Independiente de core-service
- Puede escalar horizontalmente
- Caché local reduce carga en BD transaccional

### ✅ Mantenibilidad
- Código Python simple y legible
- Documentación automática (Swagger)
- Testing sencillo con pytest

## 🔄 Actualización de Datos

### Manual
```bash
curl -X POST http://localhost:8081/sync
```

### Automática (Cron Job - opcional)
```bash
# Agregar a crontab
*/30 * * * * curl -X POST http://localhost:8081/sync
```

### Desde Frontend (JavaScript)
```javascript
const syncData = async () => {
  const response = await fetch('http://localhost:8081/sync', {
    method: 'POST'
  });
  const result = await response.json();
  console.log('Sincronización:', result);
};
```

## 🐛 Troubleshooting

### Error: "Core service unreachable"
**Solución:** Verificar que core-service esté corriendo:
```bash
curl http://localhost:8080/graphql -d '{"query":"{__typename}"}'
```

### Error: "Modelo no entrenado"
**Solución:** Ejecutar sincronización:
```bash
curl -X POST http://localhost:8081/sync
```

### Error: "Pocos datos para entrenar"
**Solución:** Ejecutar script de generación de datos:
```bash
cd scripts
python3 generar_datos_ml_realistas.py
```

### Puerto 8081 ocupado
**Solución:** Cambiar puerto en `run.sh` o matar proceso:
```bash
lsof -ti:8081 | xargs kill -9
```

## 📈 Mejoras Futuras (Opcional)

- ✅ **Cache Redis:** Reemplazar SQLite por Redis para alta concurrencia
- ✅ **Modelos más complejos:** Random Forest, XGBoost
- ✅ **Deep Learning:** Transfer Learning para imágenes de productos
- ✅ **Streaming:** Kafka para actualización en tiempo real
- ✅ **Monitoring:** Prometheus + Grafana para métricas
- ✅ **CI/CD:** Docker + GitHub Actions

## 📞 Soporte

Si encuentras problemas:

1. Verificar logs del servidor (se muestran en consola)
2. Revisar `/health` endpoint
3. Verificar que core-service tenga datos
4. Consultar documentación en `/docs`

## 🎉 Resultado Final

Después de ejecutar:
- ✅ Microservicio ML corriendo en puerto 8081
- ✅ 3 modelos entrenados automáticamente
- ✅ API REST documentada y funcional
- ✅ Integración lista con frontend
- ✅ Base de datos SQLite con caché
- ✅ Resultados útiles y entendibles

**¡Sin GPUs, sin complejidad, sin problemas!** 🚀
