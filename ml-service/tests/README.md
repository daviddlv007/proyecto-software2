# 🧪 Testing del Microservicio ML

## Guía Rápida de Testing

### 📋 Requisitos Previos

Antes de ejecutar los tests, asegúrate de tener:

1. ✅ **core-service** corriendo en `http://localhost:8080`
   ```bash
   cd core-service
   ./mvnw spring-boot:run
   ```

2. ✅ **ml-service** corriendo en `http://localhost:8081`
   ```bash
   cd ml-service
   ./run.sh
   ```

3. ✅ **Datos poblados** en core-service
   ```bash
   cd scripts
   python3 generar_datos_ml_realistas.py
   ```

---

## 🚀 Ejecutar Tests

### Método 1: Script Automatizado (Recomendado)

```bash
cd ml-service
python3 tests/test_ml_service.py
```

Este script ejecuta **automáticamente**:
- 8 grupos de tests
- ~20 verificaciones individuales
- Output con colores para fácil lectura
- Resumen final con estadísticas

### Método 2: Tests Individuales con cURL

Si prefieres probar endpoints específicos:

```bash
# 1. Health Check
curl http://localhost:8081/health

# 2. Sincronizar datos
curl -X POST http://localhost:8081/sync

# 3. Predecir precio
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "Bebidas",
    "stock": 50,
    "nombre": "Jugo Natural 1L"
  }'

# 4. Segmentación de clientes
curl http://localhost:8081/ml/segmentacion

# 5. Detección de anomalías
curl http://localhost:8081/ml/anomalias

# 6. Metadata de modelos
curl http://localhost:8081/models

# 7. Info del servicio
curl http://localhost:8081/
```

### Método 3: Swagger UI (Interactivo)

1. Abrir navegador en: http://localhost:8081/docs
2. Probar cada endpoint con la interfaz visual
3. Ver ejemplos de request/response en tiempo real

---

## 📊 Output Esperado

### ✅ Tests Exitosos

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

======================================================================
                2. HEALTH CHECK ML SERVICE
======================================================================

✓ Health endpoint
  Status: healthy
✓ Core service alcanzable

======================================================================
                3. SINCRONIZACIÓN DE DATOS
======================================================================

ℹ Iniciando sincronización (puede tardar 5-10 segundos)...
✓ Sincronización exitosa
  Completada en 5.23 segundos
✓ Productos sincronizados: 46
  Se esperaban al menos 10 productos
✓ Ventas sincronizadas: 182
  Se esperaban al menos 50 ventas
✓ Clientes sincronizados: 25
  Se esperaban al menos 10 clientes

======================================================================
                4. PREDICCIÓN DE PRECIOS (ML SUPERVISADO)
======================================================================

✓ Producto Bebidas
  Precio sugerido: $3.15
✓ Producto Lácteos
  Precio sugerido: $4.82
✓ Producto Limpieza
  Precio sugerido: $6.50

======================================================================
                5. SEGMENTACIÓN DE CLIENTES (ML NO SUPERVISADO)
======================================================================

✓ Segmentación ejecutada
  Total clientes: 25
ℹ Distribución de segmentos:
ℹ   VIP: 5 clientes
ℹ   Regular: 14 clientes
ℹ   Ocasional: 6 clientes
✓ Suma de segmentos correcta
  5 + 14 + 6 = 25

ℹ Ejemplos de clientes VIP:
ℹ   - María González: $450.50 en 15 compras
ℹ   - Carlos Rodríguez: $389.20 en 12 compras

======================================================================
                6. DETECCIÓN DE ANOMALÍAS (ML SEMI-SUPERVISADO)
======================================================================

✓ Detección ejecutada
  Ventas analizadas: 182
✓ Anomalías detectadas
  18 anomalías (9.9% del total)
✓ Porcentaje de anomalías razonable
  9.9% está dentro del rango esperado (5-20%)

ℹ Ejemplos de anomalías detectadas:
ℹ   1. Venta #45: $150.00 - Total muy alto | Muchos productos
ℹ   2. Venta #89: $2.50 - Total muy bajo
ℹ   3. Venta #123: $98.75 - Muchos productos

======================================================================
                7. METADATA DE MODELOS
======================================================================

✓ Endpoint de modelos
  3 modelos registrados
✓ Modelo 'price_predictor' registrado
✓ Modelo 'customer_segmentation' registrado
✓ Modelo 'anomaly_detector' registrado

ℹ Detalle de modelos:
ℹ   - price_predictor: 46 muestras, entrenado: 2025-10-24T11:13:14
ℹ   - customer_segmentation: 25 muestras, entrenado: 2025-10-24T11:13:14
ℹ   - anomaly_detector: 182 muestras, entrenado: 2025-10-24T11:13:15

======================================================================
                8. ENDPOINT RAÍZ (INFO)
======================================================================

✓ Endpoint raíz
  Servicio: ML Service

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

---

## ⚠️ Troubleshooting

### Error: "Core service unreachable"

**Causa:** core-service no está corriendo o no responde en puerto 8080

**Solución:**
```bash
# Verificar si está corriendo
curl http://localhost:8080/graphql -d '{"query":"{__typename}"}'

# Si no responde, iniciar core-service
cd core-service
./mvnw spring-boot:run
```

### Error: "ML service no disponible"

**Causa:** ml-service no está corriendo o no responde en puerto 8081

**Solución:**
```bash
# Verificar si está corriendo
curl http://localhost:8081/health

# Si no responde, iniciar ml-service
cd ml-service
./run.sh
```

### Error: "Sincronización falló"

**Causa:** No hay datos en core-service o GraphQL no responde

**Solución:**
```bash
# Poblar base de datos
cd scripts
python3 generar_datos_ml_realistas.py

# Verificar que hay datos
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ getAllProductos { id nombre } }"}'
```

### Error: "Pocos datos para entrenar"

**Causa:** Insuficientes registros en la base de datos

**Solución:**
```bash
# El script genera ~50 productos, ~250 ventas, ~25 clientes
cd scripts
python3 generar_datos_ml_realistas.py
```

### Error: "Modelo no entrenado"

**Causa:** No se ejecutó la sincronización inicial

**Solución:**
```bash
# Ejecutar sincronización manualmente
curl -X POST http://localhost:8081/sync
```

---

## 📈 Interpretación de Resultados

### Predicción de Precios
- **Precio sugerido:** Entre $0.50 y $100.00
- **Válido:** Si está dentro del rango de precios del catálogo
- **Útil para:** Sugerir precios para nuevos productos basándose en categoría y stock

### Segmentación de Clientes
- **VIP:** Clientes con alta frecuencia (≥4 compras) y ticket alto (≥$25)
- **Regular:** Clientes con frecuencia media (≥2 compras) y ticket medio (≥$12)
- **Ocasional:** Resto de clientes
- **Distribución esperada:** ~20% VIP, ~55% Regular, ~25% Ocasional

### Detección de Anomalías
- **Porcentaje esperado:** 5-20% de anomalías
- **Razones comunes:**
  - Total muy alto (>$100)
  - Total muy bajo (<$5)
  - Muchos productos (>10 items)
  - Ticket promedio inusual
- **Útil para:** Detectar posibles fraudes, errores de captura, comportamientos inusuales

---

## 🎯 Casos de Prueba Adicionales

Si quieres probar casos específicos:

### Predicción con diferentes categorías
```bash
# Bebidas (precio bajo)
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{"categoria": "Bebidas", "stock": 100, "nombre": "Agua"}'

# Limpieza (precio medio)
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{"categoria": "Limpieza", "stock": 50, "nombre": "Detergente"}'

# Congelados (precio alto)
curl -X POST http://localhost:8081/predict/price \
  -H "Content-Type: application/json" \
  -d '{"categoria": "Congelados", "stock": 20, "nombre": "Pizza"}'
```

### Verificar sincronización reciente
```bash
# Ver metadata de modelos para fecha de entrenamiento
curl http://localhost:8081/models | python3 -m json.tool
```

### Re-sincronizar para actualizar datos
```bash
# Útil después de agregar más datos al core-service
curl -X POST http://localhost:8081/sync
```

---

## ✅ Checklist de Testing

Antes de considerar el microservicio listo:

- [ ] Health check responde correctamente
- [ ] Sincronización completa sin errores
- [ ] Al menos 10 productos sincronizados
- [ ] Al menos 50 ventas sincronizadas
- [ ] Al menos 10 clientes sincronizados
- [ ] 3 modelos entrenados y registrados
- [ ] Predicción de precios devuelve valores razonables
- [ ] Segmentación identifica 3 tipos de clientes
- [ ] Detección de anomalías encuentra 5-20% de casos
- [ ] Todos los endpoints responden en <2 segundos
- [ ] Documentación Swagger accesible en /docs

---

## 📞 Próximos Pasos

Después de verificar que todos los tests pasan:

1. **Integrar con Frontend:**
   - Crear componente `MLDashboard.tsx`
   - Consumir endpoints desde React
   - Visualizar predicciones y segmentación

2. **Deployment:**
   - Dockerizar el servicio
   - Configurar CI/CD
   - Deploy en producción

3. **Mejoras:**
   - Agregar más features a los modelos
   - Implementar cache Redis
   - Agregar monitoreo con Prometheus

---

**¡Listo para integrar con el frontend!** 🚀
