## Configuración de Conexiones a BD - BI-Service

### Resumen de cambios
Se modularizó la conexión a las bases de datos en el BI-service para permitir despliegue en instancias separadas sin modificar código fuente.

### Ubicación de variables de entorno
Todas las variables de conexión están centralizadas en `.env`:

```env
# Core Database (donde están los datos transaccionales del negocio)
CORE_DB_HOST=postgres          # URL/IP del servidor core-service BD
CORE_DB_PORT=5432
CORE_DB_NAME=coredb
CORE_DB_USER=postgres
CORE_DB_PASSWORD=postgres

# BI Service Database (BD interna del BI-service)
BI_DB_HOST=localhost
BI_DB_PORT=5432
BI_DB_NAME=software2_DB
BI_DB_USER=postgres
BI_DB_PASSWORD=postgres
```

### Módulo centralizado: `config/db_config.py`

Proporciona funciones para acceder a ambas bases de datos de forma consistente:

```python
from config.db_config import (
    get_core_raw_connection(),      # Conexión raw Django a core-service BD
    get_core_sqlalchemy_engine(),   # SQLAlchemy engine para core-service BD
    get_core_db_config(),           # Diccionario de configuración core-service
    get_bi_db_config(),             # Diccionario de configuración BI-service
)
```

### Dónde se usa cada conexión

#### Core-service BD (datos transaccionales):
- `prep/views.py`: Métricas y análisis de esquemas cargados
- `notifications/views.py`: Dropdowns de tablas/columnas en formularios KPI
- `notifications/services.py`: Cálculo de valores KPI y validaciones

#### BI-service BD (datos internos):
- Modelos Django (DataSource, UploadedDataset, Diagrama)
- Metadata de archivos cargados
- Configuración interna del BI

### Despliegue en instancias separadas

En producción, si cada microservicio está en una máquina diferente:

1. **Core-service VM**: Tiene PostgreSQL con la BD `coredb`
   - Host: `192.168.1.10` (ejemplo)
   - Puerto: `5432`

2. **BI-service VM**: Tiene su propia PostgreSQL para BD interna
   - Modifica `.env`:
     ```env
     CORE_DB_HOST=192.168.1.10    # IP del server core-service
     CORE_DB_PORT=5432
     CORE_DB_NAME=coredb
     CORE_DB_USER=postgres
     CORE_DB_PASSWORD=secure_password
     
     BI_DB_HOST=localhost          # BD local del BI
     BI_DB_PORT=5432
     BI_DB_NAME=software2_DB
     BI_DB_USER=postgres
     BI_DB_PASSWORD=secure_password
     ```

3. Reinicia el BI-service:
   ```bash
   docker-compose restart bi-service
   ```

### Cambios realizados

1. **Creado**: `bi-service/config/db_config.py`
   - Módulo centralizado de configuración de conexiones
   - Usa variables de entorno para máxima flexibilidad

2. **Modificado**: `bi-service/prep/views.py`
   - Reemplazó `from django.db import connection` con `get_core_raw_connection()`
   - Ahora consulta core-service BD en lugar de BI-service BD

3. **Modificado**: `bi-service/notifications/views.py`
   - AJAX endpoints `get_tables_ajax` y `get_columns_by_table_ajax`
   - Ahora usan `get_core_raw_connection()` para obtener data del core-service

4. **Modificado**: `bi-service/notifications/services.py`
   - KPICalculator usa `get_core_raw_connection()` para calcular KPIs
   - Validación de columnas ocurre en core-service BD

5. **Actualizado**: `.env`
   - Agregadas variables `CORE_DB_*` y `BI_DB_*`
   - Variables ya existentes en `config/settings.py` se usan desde aquí

### Testing

Los cambios fueron verificados:
- Endpoint `GET /notifications/kpi/create/`: ✅ 200 OK
- Endpoint `GET /prep/public/`: ✅ 200 OK
- Servicio BI levanta sin errores de conexión

