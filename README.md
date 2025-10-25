# 🛒 Sistema de Supermercado con Machine Learning & Deep Learning

> **Sistema completo de gestión con 3 servicios de IA integrados**  
> Spring Boot + FastAPI + Node.js + React + Docker

---

## 📊 Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                       │
│                         Puerto: 5173                               │
│  • Dashboard con gráficas (Recharts)                               │
│  • CRUD: Productos, Ventas, Clientes, Categorías, Usuarios        │
│  • ML: Predicción, Segmentación, Anomalías                        │
│  • DL: Clasificación de imágenes, LSTM, Recomendaciones           │
└──────────────┬──────────────────────────┬──────────────────────────┘
               │                          │
               │ GraphQL                  │ REST APIs
               │                          │
    ┌──────────▼────────────┐   ┌─────────▼─────────┬──────────────┐
    │   CORE SERVICE        │   │   ML SERVICE      │  DL SERVICE  │
    │   Spring Boot 3.5     │   │   FastAPI         │  Node.js 20  │
    │   Puerto: 8080        │───│   Puerto: 8081    │  Puerto: 8082│
    │                       │   │                   │              │
    │ • GraphQL API         │   │ • Predicción $    │ • MobileNet  │
    │ • JWT Auth            │   │ • Segmentación    │ • LSTM       │
    │ • H2 (Dev)            │   │ • Anomalías       │ • Autoencoder│
    │ • 6 Entidades         │   │ • scikit-learn    │ • TensorFlow │
    │                       │   │ • SQLite Cache    │ • In-Memory  │
    └───────────────────────┘   └───────────────────┴──────────────┘
```

---

## 🚀 Inicio Rápido

### ⚡ Opción 1: Makefile (MÁS RÁPIDO)

```bash
# Ver comandos disponibles
make help

# 🎯 Todo desde cero (build + start + init + URLs)
make dev

# 🚀 Inicio rápido (solo start)
make quick

# 📊 Ver estado
make status

# 🏥 Health checks
make health
```

**Comandos más usados:**
```bash
make start          # Levantar servicios
make stop           # Detener servicios
make restart        # Reiniciar servicios
make logs           # Ver logs en tiempo real
make init           # Inicialización completa (datos + ML/DL)
make populate       # Solo poblar datos
make clean          # Limpiar base de datos
make reset          # Limpiar + poblar
make urls           # Mostrar URLs de acceso
```

### 🐳 Opción 2: Docker Compose Directo

```bash
# 1. Levantar todos los servicios
docker-compose up -d

# 2. Verificar estado (esperar que estén "healthy")
docker-compose ps

# 3. Acceder al sistema
open http://localhost:5173
```

**URLs de los servicios:**
- **Frontend**: http://localhost:5173
- **Core API**: http://localhost:8080/graphiql
- **ML API**: http://localhost:8081/docs
- **DL API**: http://localhost:8082
- **H2 Console**: http://localhost:8080/h2-console

### 🛠️ Opción 3: Manual (Sin Docker)

**Terminal 1 - Core Service:**
```bash
cd core-service
./mvnw spring-boot:run
```

**Terminal 2 - ML Service:**
```bash
cd ml-service
pip install -r requirements.txt
./run.sh
```

**Terminal 3 - DL Service:**
```bash
cd dl-service
npm install
npm run dev
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 💾 Persistencia de Datos

### Arquitectura Database per Service

```
CORE SERVICE (Fuente de Verdad)
├─ Base de datos: H2 (dev) / PostgreSQL (prod)
├─ Ubicación: /data/core_db
├─ Entidades: Productos, Ventas, Clientes, Categorías, Usuarios
└─ Volumen Docker: core-db-data

ML SERVICE (Cache + Modelos)
├─ Base de datos: SQLite
├─ Ubicación: /data/ml_cache.db
├─ Contenido: Snapshots de productos/ventas, modelos entrenados
└─ Volúmenes Docker: ml-db-data, ml-models

DL SERVICE (Modelos + Embeddings)
├─ Base de datos: In-Memory (dev) / SQLite (prod)
├─ Ubicación: /data/dl_cache.db
├─ Contenido: Embeddings, matrices de co-compra, modelos DL
└─ Volúmenes Docker: dl-models, dl-uploads
```

### Sincronización de Datos

```
1. Core Service ← Script Python (generar_datos_ml_realistas.py)
   └─> Inserta: 46 productos, 172 ventas, 25 clientes

2. ML Service ← Pull desde Core (GraphQL)
   └─> POST /sync → Copia datos a cache local

3. DL Service ← Pull lazy (GraphQL)
   └─> Consulta bajo demanda durante entrenamiento
```

### Comandos de Gestión

```bash
# Ver volúmenes persistentes
docker volume ls

# Inspeccionar volumen específico
docker volume inspect proyecto-parcial2-sw2_core-db-data

# Backup de base de datos
docker run --rm -v proyecto-parcial2-sw2_core-db-data:/data \
    -v $(pwd)/backups:/backup alpine \
    tar czf /backup/core-db-$(date +%Y%m%d).tar.gz /data

# Restaurar backup
docker run --rm -v proyecto-parcial2-sw2_core-db-data:/data \
    -v $(pwd)/backups:/backup alpine \
    tar xzf /backup/core-db-20251025.tar.gz -C /

# CUIDADO: Eliminar todos los datos
docker-compose down -v
```

---

## 📋 Inicialización de Datos

### Scripts Disponibles

**1. Inicialización Completa (Recomendado)**
```bash
cd scripts
./inicializacion_completa.sh
```
**Funciones:**
- ✅ Verifica servicios activos (health checks)
- ✅ Detecta si hay datos existentes
- ✅ **Pregunta** si quieres regenerar (limpia + genera)
- ✅ Sincroniza con ML Service
- ✅ Entrena modelos ML/DL
- ✅ Verifica estado final

**2. Solo Generar Datos**
```bash
cd scripts
python3 generar_datos_ml_realistas.py
```
**Genera:**
- 46 productos reales (Coca-Cola, Pan, Yogurt, etc.)
- 10 categorías (Bebidas, Lácteos, Carnes, etc.)
- 25 clientes con patrones de compra
- 172 ventas distribuidas en 3 meses
- Datos coherentes para ML/DL

⚠️ **Nota:** No limpia datos anteriores, puede generar duplicados.

**3. Solo Limpiar Datos**
```bash
cd scripts
./limpiar_datos.sh
```
**Limpia:**
- Elimina todas las ventas
- Elimina todos los clientes
- Elimina todos los productos
- Mantiene categorías y estructura

**Modo silencioso (para scripts):**
```bash
./limpiar_datos.sh --silent
```

### Flujo Recomendado

```bash
# Primera vez: Inicialización completa
./inicializacion_completa.sh

# Limpiar y regenerar manualmente:
./limpiar_datos.sh
python3 generar_datos_ml_realistas.py

# Solo limpiar (para testing):
./limpiar_datos.sh
```

---

## 🛠️ Makefile - Comandos Rápidos

El proyecto incluye un **Makefile** con los comandos más comunes para facilitar el desarrollo.

### Comandos Principales

```bash
# 📖 Ver todos los comandos disponibles
make help

# 🎯 Desarrollo desde cero
make dev              # Build + Start + Init + URLs (TODO)

# 🚀 Inicio/Parada
make start            # Levantar servicios
make stop             # Detener servicios  
make restart          # Reiniciar servicios
make down             # Detener y eliminar contenedores
make quick            # Inicio rápido (start + URLs)

# 🔨 Build
make build            # Construir imágenes
make rebuild          # Down + Build + Start
make up               # Build + Start

# 💾 Gestión de Datos
make init             # Inicialización completa (servicios + datos + ML/DL)
make populate         # Solo poblar datos (sin limpiar)
make clean            # Limpiar base de datos
make reset            # Limpiar + poblar (reset completo)

# 📊 Monitoreo
make status           # Ver estado de servicios
make logs             # Ver logs en tiempo real
make logs-core        # Logs del Core Service
make logs-ml          # Logs del ML Service
make logs-dl          # Logs del DL Service
make logs-frontend    # Logs del Frontend
make health           # Health checks de todos los servicios

# 🧹 Limpieza Profunda (CUIDADO)
make clean-volumes    # Eliminar volúmenes (DESTRUCTIVO)
make clean-all        # Limpieza total (contenedores + volúmenes + imágenes)

# 🧪 Testing
make test             # Ejecutar todos los tests

# 🔗 Utilidades
make urls             # Mostrar URLs de acceso
make shell-core       # Shell en Core Service
make shell-ml         # Shell en ML Service
make shell-dl         # Shell en DL Service
make shell-frontend   # Shell en Frontend
```

### Ejemplos de Uso

**Primera vez - Setup completo:**
```bash
make dev
# Equivale a: build + start + init + mostrar URLs
```

**Desarrollo diario:**
```bash
make start            # Levantar servicios
make health           # Verificar que todo esté OK
make logs-core        # Ver logs si hay problemas
```

**Testing/Demos:**
```bash
make reset            # Limpiar + regenerar datos
make populate         # Solo agregar más datos
```

**Rebuild después de cambios:**
```bash
make rebuild          # Down + Build + Start
```

---

## 🧠 Modelos de Machine Learning

### ML Service (scikit-learn)

**1. Predicción de Precios (Regresión Lineal)**
```python
# Entrada: categoría, stock, peso_aprox
# Salida: precio_predicho
# Accuracy: R² > 0.85
```

**2. Segmentación de Clientes (K-Means)**
```python
# Entrada: total_compras, frecuencia, recencia
# Salida: segmento (VIP, Regular, Ocasional)
# Clusters: 3
```

**3. Detección de Anomalías (Isolation Forest)**
```python
# Entrada: cantidad, precio_unitario, total
# Salida: is_anomaly, score
# Threshold: contamination=0.1
```

### DL Service (TensorFlow.js)

**1. Clasificación de Imágenes (MobileNet v2)**
```typescript
// Entrada: imagen 224x224
// Salida: top-5 productos similares
// Red: CNN pre-entrenada (ImageNet)
```

**2. Predicción de Ventas (LSTM)**
```typescript
// Entrada: 7 días históricos
// Salida: 7 días futuros
// Arquitectura: LSTM(16) + Dropout(0.2) + Dense(7)
// Épocas: 50
```

**3. Recomendaciones (Autoencoder)**
```typescript
// Entrada: id_producto
// Salida: top-5 productos similares
// Técnica: Collaborative Filtering + Embeddings (32D)
// Similitud: Cosine similarity
```

---

## 🎯 Características por Servicio

### Core Service (Spring Boot)
- ✅ GraphQL API con 6 entidades
- ✅ Autenticación JWT
- ✅ Spring Data JPA + Hibernate
- ✅ H2 Console habilitado
- ✅ Actuator para health checks
- ✅ CORS configurado

### ML Service (FastAPI)
- ✅ 3 modelos supervisados/no supervisados
- ✅ Caché SQLite para performance
- ✅ Swagger UI automático
- ✅ Sincronización con Core Service
- ✅ Modelos persistentes (.pkl)

### DL Service (Node.js)
- ✅ TensorFlow.js nativo
- ✅ 3 redes neuronales profundas
- ✅ Procesamiento de imágenes
- ✅ Hot reload con ts-node-dev
- ✅ Embeddings en memoria

### Frontend (React)
- ✅ TypeScript + Vite
- ✅ Apollo Client (GraphQL)
- ✅ Recharts para gráficas
- ✅ JWT Auth + Protected Routes
- ✅ 7 páginas completas
- ✅ Hot Module Replacement

---

## 🛠️ Comandos Docker

### Desarrollo

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio
docker-compose logs -f core-service

# Verificar estado
docker-compose ps

# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Rebuild de un servicio
docker-compose up -d --build core-service

# Rebuild completo
docker-compose up -d --build

# Ejecutar comando en contenedor
docker-compose exec core-service sh

# Ver recursos
docker stats
```

### Troubleshooting

```bash
# Ver errores de un servicio
docker-compose logs --tail 100 core-service

# Reiniciar un servicio
docker-compose restart core-service

# Verificar health checks
docker inspect --format='{{.State.Health.Status}}' core-service

# Limpiar todo (DESTRUCTIVO)
docker-compose down -v
docker system prune -a --volumes

# Verificar conectividad entre servicios
docker-compose exec frontend ping core-service
```

---

## 🔧 Configuración de Entorno

### Variables de Entorno (.env)

```bash
# Puertos
CORE_PORT=8080
ML_PORT=8081
DL_PORT=8082
FRONTEND_PORT=5173

# URLs (para frontend)
CORE_API_URL=http://localhost:8080/graphql
ML_API_URL=http://localhost:8081
DL_API_URL=http://localhost:8082

# Base de datos (producción)
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme
POSTGRES_DB_CORE=core_db
POSTGRES_DB_ML=ml_db
POSTGRES_DB_DL=dl_db
```

### Recursos del Sistema

**Desarrollo (docker-compose.yml):**
- Total RAM: ~1GB
- Total CPU: 3 cores
- Inicio: <20 segundos

**Producción (docker-compose.prod.yml):**
- Total RAM: ~2.5GB
- Total CPU: 5 cores
- Bases de datos: PostgreSQL

---

## 📦 Estructura del Proyecto

```
proyecto-parcial2-sw2/
├── core-service/          # Spring Boot + GraphQL
│   ├── src/main/java/     # Código fuente
│   ├── src/main/resources/
│   │   └── graphql/       # Schema GraphQL
│   ├── Dockerfile         # Multi-stage build
│   └── pom.xml            # Maven
│
├── ml-service/            # FastAPI + scikit-learn
│   ├── app/
│   │   ├── main.py        # API endpoints
│   │   ├── services/      # Modelos ML
│   │   └── database.py    # SQLite
│   ├── Dockerfile
│   └── requirements.txt
│
├── dl-service/            # Node.js + TensorFlow.js
│   ├── src/
│   │   ├── server-production.ts
│   │   └── services/      # Redes neuronales
│   ├── Dockerfile.dev     # Hot reload
│   └── package.json
│
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── pages/         # 7 páginas
│   │   ├── components/    # Componentes reutilizables
│   │   ├── apollo/        # GraphQL client
│   │   └── api/           # REST clients
│   ├── Dockerfile.dev     # Vite dev server
│   └── package.json
│
├── scripts/               # Utilidades
│   ├── generar_datos_ml_realistas.py
│   └── limpiar_datos.sh
│
├── docker-compose.yml     # Desarrollo
├── docker-compose.prod.yml # Producción
└── README.md              # Este archivo
```

---

## 🧪 Testing

### Core Service (JUnit + Spring Boot Test)
```bash
cd core-service
./mvnw test
```

### ML Service (pytest)
```bash
cd ml-service/tests
pytest test_ml_service.py -v
```

### DL Service (Jest / Manual)
```bash
cd dl-service/tests
python3 test_api_completo.py
```

### Frontend (Vitest)
```bash
cd frontend
npm run test
```

---

## 🐛 Problemas Comunes

### 1. Servicios no inician
```bash
# Verificar logs
docker-compose logs -f

# Verificar puertos ocupados
lsof -i :8080
lsof -i :8081
lsof -i :8082
lsof -i :5173

# Liberar puertos
kill -9 $(lsof -t -i:8080)
```

### 2. Base de datos vacía
```bash
# Inicializar datos
cd scripts
python3 generar_datos_ml_realistas.py
```

### 3. Hot reload no funciona
```bash
# Verificar volúmenes montados
docker-compose config

# Reiniciar con rebuild
docker-compose up -d --build
```

### 4. Error de memoria (WSL2)
```bash
# Editar ~/.wslconfig
[wsl2]
memory=4GB
processors=4
swap=8GB
kernelCommandLine=vsock.max_dgram_qlen=512

# Reiniciar WSL
wsl --shutdown
```

### 5. GraphQL no responde
```bash
# Verificar health check
curl http://localhost:8080/actuator/health

# Ver logs detallados
docker-compose logs -f core-service
```

---

## 📚 Tecnologías Utilizadas

### Backend
- **Java 17** + Spring Boot 3.5.6
- **Python 3.11** + FastAPI 0.115
- **Node.js 20** + TypeScript 5
- **GraphQL** (Spring GraphQL)
- **REST** (FastAPI + Express)

### Machine Learning
- **scikit-learn** 1.5+ (ML clásico)
- **TensorFlow.js** 4.x (Deep Learning)
- **pandas** + **numpy** (procesamiento)

### Frontend
- **React 18** + **TypeScript**
- **Vite 6** (build tool)
- **Apollo Client** (GraphQL)
- **Recharts** (gráficas)
- **React Router** (navegación)

### Bases de Datos
- **H2** (desarrollo)
- **PostgreSQL 15** (producción)
- **SQLite** (cache)

### DevOps
- **Docker** + **Docker Compose**
- **Multi-stage builds**
- **Health checks**
- **Hot reload**

---

## 🎓 Casos de Uso

### 1. Dashboard Ejecutivo
- Ver métricas en tiempo real
- Gráficas de ventas por categoría
- Top 10 productos más vendidos
- Tendencias de ventas (30 días)

### 2. Gestión de Inventario
- CRUD completo de productos
- Control de stock
- Categorización
- Búsqueda y filtros

### 3. Machine Learning
- Predicción de precios óptimos
- Segmentación de clientes (RFM)
- Detección de ventas anómalas

### 4. Deep Learning
- Clasificación de productos por foto
- Predicción de ventas futuras (LSTM)
- Recomendaciones personalizadas

### 5. Gestión de Ventas
- Registro de ventas
- Detalles por producto
- Histórico por cliente
- Reportes y análisis

---

## 🚀 Roadmap Futuro

- [ ] Autenticación OAuth2 (Google, Facebook)
- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Dashboard en tiempo real con actualización automática
- [ ] Reportes PDF exportables
- [ ] API Gateway con rate limiting
- [ ] Kubernetes deployment
- [ ] CI/CD con GitHub Actions
- [ ] Monitoreo con Prometheus + Grafana
- [ ] Logging centralizado (ELK Stack)
- [ ] Cache distribuido (Redis)

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👥 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

---

## 📞 Soporte

Para reportar bugs o solicitar features, crear un issue en GitHub:
https://github.com/daviddlv007/proyecto-software2/issues

---

**Última actualización**: Octubre 25, 2025  
**Versión**: 2.0.0  
**Estado**: ✅ Producción
