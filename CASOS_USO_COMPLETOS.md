# 📋 Casos de Uso del Sistema de Supermercado

## 🎯 Visión General

Este documento detalla todos los casos de uso implementados y planificados en el sistema de gestión de supermercado con integración de Machine Learning y Deep Learning.

---

## 🏪 Sistema de Gestión

### CU01
**Nombre:** Gestionar Productos
**Propósito:** Administrar completamente el catálogo de productos incluyendo inventario y categorización.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El administrador debe estar autenticado en el sistema.
**Flujo Principal:**
- **Crear Producto:**
  1. Acceder a la opción de crear producto.
  2. Ingresar nombre, descripción, precio, stock y seleccionar categoría.
  3. Cargar URL de imagen (opcional).
  4. Confirmar creación del producto.
  5. Recibir confirmación de creación exitosa.
- **Leer/Listar Productos:**
  1. Acceder a la lista de productos.
  2. Aplicar filtros de búsqueda (opcional).
  3. El sistema muestra productos en tabla con paginación.
  4. Visualizar detalles de productos individuales.
- **Actualizar Producto:**
  1. Seleccionar producto a modificar.
  2. Editar campos (nombre, precio, stock, categoría, etc.).
  3. Confirmar cambios.
  4. Recibir confirmación de actualización.
- **Eliminar Producto:**
  1. Seleccionar producto a eliminar.
  2. Confirmar eliminación.
  3. El sistema valida que no tenga ventas asociadas.
  4. Recibir confirmación de eliminación.
**Postcondición:** El catálogo de productos queda actualizado con las operaciones realizadas.
**Excepción:** Datos incompletos, validaciones fallidas, productos con dependencias o errores de conexión.
**Plataforma:** web
**Microservicio:** Core Service

### CU02
**Nombre:** Gestionar Ventas
**Propósito:** Administrar el proceso completo de ventas con control automático de inventario.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El administrador debe estar autenticado y existir clientes registrados.
**Flujo Principal:**
- **Crear Venta:**
  1. Acceder a la opción de crear venta.
  2. Seleccionar cliente existente.
  3. Agregar productos con cantidades.
  4. El sistema valida stock disponible automáticamente.
  5. Calcular totales y subtotales.
  6. Confirmar venta.
  7. Recibir confirmación con descuento de inventario.
- **Leer/Listar Ventas:**
  1. Acceder al historial de ventas.
  2. Aplicar filtros por fecha, cliente, etc.
  3. Visualizar lista de ventas con detalles.
  4. Ver detalles específicos de cada venta.
- **Actualizar Venta:**
  1. Seleccionar venta a modificar.
  2. El sistema restaura stock de productos anteriores.
  3. Modificar productos y cantidades.
  4. Validar nuevo stock disponible.
  5. Recalcular totales.
  6. Confirmar actualización.
- **Eliminar Venta:**
  1. Seleccionar venta a cancelar.
  2. Confirmar eliminación.
  3. El sistema restaura stock automáticamente.
  4. Recibir confirmación de cancelación.
**Postcondición:** Las ventas quedan registradas/actualizadas con control automático de inventario.
**Excepción:** Stock insuficiente, datos incompletos, errores de validación o problemas de transacción.
**Plataforma:** web
**Microservicio:** Core Service

### CU03
**Nombre:** Gestionar Clientes
**Propósito:** Administrar la base de datos completa de clientes del sistema.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El administrador debe estar autenticado en el sistema.
**Flujo Principal:**
- **Crear Cliente:**
  1. Acceder a la opción de crear cliente.
  2. Ingresar nombre, correo electrónico y teléfono.
  3. El sistema valida formato de correo.
  4. Confirmar creación.
  5. Recibir confirmación de registro.
- **Leer/Listar Clientes:**
  1. Acceder a la lista de clientes.
  2. Aplicar filtros de búsqueda por nombre o correo.
  3. Visualizar clientes en tabla.
  4. Ver detalles individuales de clientes.
- **Actualizar Cliente:**
  1. Seleccionar cliente a modificar.
  2. Editar información de contacto.
  3. Confirmar cambios.
  4. Recibir confirmación de actualización.
- **Eliminar Cliente:**
  1. Seleccionar cliente a eliminar.
  2. El sistema valida que no tenga ventas asociadas.
  3. Confirmar eliminación.
  4. Recibir confirmación de eliminación.
**Postcondición:** La base de datos de clientes queda actualizada.
**Excepción:** Datos inválidos, correos duplicados, clientes con dependencias o errores de validación.
**Plataforma:** web
**Microservicio:** Core Service

### CU04
**Nombre:** Gestionar Categorías
**Propósito:** Administrar las categorías de productos para organización del catálogo.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El administrador debe estar autenticado en el sistema.
**Flujo Principal:**
- **Crear Categoría:**
  1. Acceder a la opción de crear categoría.
  2. Ingresar nombre y descripción.
  3. Confirmar creación.
  4. Recibir confirmación de registro.
- **Leer/Listar Categorías:**
  1. Acceder a la lista de categorías.
  2. Visualizar jerarquía de categorías.
  3. Ver detalles de cada categoría.
- **Actualizar Categoría:**
  1. Seleccionar categoría a modificar.
  2. Editar nombre y descripción.
  3. Confirmar cambios.
  4. Recibir confirmación de actualización.
- **Eliminar Categoría:**
  1. Seleccionar categoría a eliminar.
  2. El sistema valida que no tenga productos asociados.
  3. Confirmar eliminación.
  4. Recibir confirmación de eliminación.
**Postcondición:** La estructura de categorías queda actualizada.
**Excepción:** Datos incompletos, categorías con dependencias o errores de validación.
**Plataforma:** web
**Microservicio:** Core Service

### CU05
**Nombre:** Gestionar Usuarios
**Propósito:** Administrar usuarios del sistema con control de acceso y seguridad.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El administrador debe estar autenticado con permisos de administración.
**Flujo Principal:**
- **Crear Usuario:**
  1. Acceder a la opción de crear usuario.
  2. Ingresar nombre, correo y contraseña.
  3. El sistema encripta la contraseña automáticamente.
  4. Confirmar creación.
  5. Recibir confirmación de registro.
- **Leer/Listar Usuarios:**
  1. Acceder a la lista de usuarios.
  2. Visualizar usuarios registrados.
  3. Ver detalles de cada usuario (sin contraseñas).
- **Actualizar Usuario:**
  1. Seleccionar usuario a modificar.
  2. Editar nombre y correo.
  3. Cambiar contraseña (opcional).
  4. Confirmar cambios.
  5. Recibir confirmación de actualización.
- **Eliminar Usuario:**
  1. Seleccionar usuario a eliminar.
  2. El sistema valida permisos de eliminación.
  3. Confirmar eliminación.
  4. Recibir confirmación de eliminación.
**Postcondición:** Los usuarios del sistema quedan actualizados con seguridad.
**Excepción:** Datos inválidos, permisos insuficientes o errores de encriptación.
**Plataforma:** web
**Microservicio:** Core Service

## 🤖 Machine Learning

### CU06
**Nombre:** Predecir Precio Óptimo
**Propósito:** Sugerir precios óptimos para nuevos productos usando modelos de regresión.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El servicio ML debe estar disponible y con modelos entrenados.
**Flujo Principal:**
1. Acceder a la funcionalidad de predicción de precios.
2. Ingresar categoría, stock y nombre del producto.
3. El sistema envía datos al servicio ML.
4. Recibir predicción con precio sugerido y confianza.
5. Mostrar características utilizadas en la predicción.
**Postcondición:** La predicción de precio queda disponible para referencia.
**Excepción:** Servicio ML no disponible, datos insuficientes o error en la predicción.
**Plataforma:** web
**Microservicio:** ML Service

### CU07
**Nombre:** Segmentar Clientes (RFM)
**Propósito:** Clasificar automáticamente clientes en segmentos usando análisis RFM.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** Deben existir datos de clientes y compras para análisis.
**Flujo Principal:**
1. Acceder a la funcionalidad de segmentación.
2. El sistema procesa datos RFM (Recency, Frequency, Monetary).
3. Aplicar algoritmo K-Means para clustering.
4. Generar segmentos: VIP, Regular, Ocasional.
5. Mostrar estadísticas y lista detallada de clientes.
**Postcondición:** Los clientes quedan segmentados para estrategias de marketing.
**Excepción:** Datos insuficientes, error en el algoritmo o problemas de conectividad.
**Plataforma:** web
**Microservicio:** ML Service

### CU08
**Nombre:** Detectar Anomalías en Ventas
**Propósito:** Identificar ventas inusuales usando algoritmos de detección de anomalías.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** Deben existir datos históricos de ventas para análisis.
**Flujo Principal:**
1. Acceder a la detección de anomalías.
2. El sistema analiza todas las ventas registradas.
3. Aplicar Isolation Forest para detectar patrones anómalos.
4. Generar score de anomalía y razones identificadas.
5. Mostrar lista de ventas sospechosas con detalles.
**Postcondición:** Las anomalías detectadas quedan disponibles para revisión.
**Excepción:** Datos insuficientes, error en el modelo o problemas de procesamiento.
**Plataforma:** web
**Microservicio:** ML Service

---

## 🧠 Deep Learning

### CU09
**Nombre:** Análisis Inteligente de Productos
**Propósito:** Realizar análisis multimodal de productos utilizando Deep Learning, con entradas flexibles y salidas especializadas.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El servicio DL debe estar operativo con modelos cargados.
**Flujo Principal:**
- **Entrada por Imagen:**
  1. Cargar imagen del producto.
  2. El sistema envía imagen al servicio DL.
  3. Procesar con modelo MobileNet v2.
  4. **Salida:** Mostrar producto identificado con confianza y predicciones alternativas.
- **Entrada por Datos Históricos:**
  1. Seleccionar producto y período de análisis.
  2. El sistema procesa datos históricos con LSTM.
  3. **Salida:** Generar pronóstico de ventas con intervalos de confianza y tendencias.
- **Entrada por Análisis Completo:**
  1. Seleccionar producto para análisis multimodal.
  2. Combinar clasificación por imagen, predicción de ventas y recomendaciones.
  3. El sistema analiza patrones con autoencoder.
  4. **Salida:** Mostrar resultados integrados: identificación, predicción y recomendaciones personalizadas.
**Postcondición:** El análisis del producto queda completo con múltiples perspectivas.
**Excepción:** Datos insuficientes, modelos no disponibles o errores de procesamiento.
**Plataforma:** web
**Microservicio:** DL Service

---

## 📊 BI (Business Intelligence)

### CU10
**Nombre:** Dashboard y Visualizaciones BI
**Propósito:** Gestionar dashboards ejecutivos, gráficos y diagramas personalizados con soporte para creación manual y automática con IA.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** El MicroservicioBI debe estar operativo y conectado a las bases de datos.
**Flujo Principal:**
- **Dashboard Ejecutivo:**
  1. Acceder al dashboard ejecutivo.
  2. Cargar métricas avanzadas desde múltiples fuentes.
  3. Mostrar KPIs en tiempo real con indicadores visuales.
  4. Interactuar con datos mediante filtros y drill-down.
- **Gestión de Gráficos:**
  1. Acceder al módulo de gráficos.
  2. Seleccionar tipo de diagrama y configurar fuentes de datos.
  3. Personalizar colores, etiquetas y formato.
  4. Guardar y publicar diagramas.
- **Diagramas con IA:**
  1. Seleccionar conjunto de datos.
  2. Aplicar algoritmos de IA para generar diagramas automáticamente.
  3. Permitir ajustes manuales.
  4. Guardar y compartir diagramas generados.
- **Creación Manual:**
  1. Acceder al editor de diagramas.
  2. Diseñar diagramas mediante arrastrar y soltar.
  3. Configurar propiedades visuales y datos.
  4. Guardar y versionar diagramas.
**Postcondición:** Los dashboards y diagramas quedan disponibles para análisis y toma de decisiones.
**Excepción:** Configuración inválida, datos no disponibles o errores de conexión.
**Plataforma:** web
**Microservicio:** MicroservicioBI

### CU11
**Nombre:** Monitoreo y Exploración de Datos BI
**Propósito:** Configurar alarmas, monitorear KPIs y explorar datos almacenados en las bases de datos del sistema.
**Actor Principal:** Administrador
**Actor Iniciador:** Administrador
**Precondición:** Definición previa de KPIs y permisos de acceso a bases de datos.
**Flujo Principal:**
- **Sistema de Alarmas y KPIs:**
  1. Acceder a la configuración de KPIs.
  2. Definir métricas y umbrales de alerta.
  3. Configurar notificaciones (email, dashboard).
  4. Monitorear KPIs en tiempo real y generar alertas.
- **Exploración de Datos:**
  1. Acceder al explorador de datos.
  2. Seleccionar bases de datos y tablas.
  3. Aplicar filtros y criterios de búsqueda.
  4. Ejecutar consultas y visualizar resultados.
  5. Exportar datos si necesario.
**Postcondición:** El sistema de monitoreo queda operativo y los datos explorados disponibles para análisis.
**Excepción:** Configuración inválida, permisos insuficientes o errores de consulta.
**Plataforma:** web
**Microservicio:** MicroservicioBI

---

## 📱 Aplicación Móvil

### CU12
**Nombre:** Gestión de Entregas y Pagos Móviles
**Propósito:** Gestionar entregas con GPS y procesar pagos mediante QR y tarjetas en la aplicación móvil.
**Actor Principal:** Repartidor/Cliente
**Actor Iniciador:** Repartidor/Cliente
**Precondición:** Autenticación en app móvil, GPS habilitado para entregas, acceso a cámara para pagos.
**Flujo Principal:**
- **Delivery con GPS:**
  1. Recibir notificación de entrega asignada.
  2. Activar GPS para seguimiento en tiempo real.
  3. Visualizar ruta óptima hacia la dirección.
  4. Actualizar estado de entrega y confirmar recepción.
- **Pago por QR y Tarjeta:**
  1. Seleccionar productos para compra.
  2. Escanear código QR o capturar datos de tarjeta.
  3. Seleccionar método de pago y confirmar transacción.
**Postcondición:** Las entregas quedan completadas con seguimiento y los pagos procesados.
**Excepción:** GPS no disponible, códigos QR inválidos, errores de pago o dirección inválida.
**Plataforma:** móvil
**Microservicio:** Frontend

### CU13
**Nombre:** Funcionalidades IA y BI en Móvil
**Propósito:** Acceder a diagramas BI, generar listas de compra por voz y utilizar funciones de IA en dispositivos móviles.
**Actor Principal:** Cliente/Administrador
**Actor Iniciador:** Cliente/Administrador
**Precondición:** Conexión a internet, permisos de micrófono/audio, servicios ML/DL/BI operativos.
**Flujo Principal:**
- **Mostrar Diagramas BI:**
  1. Acceder a sección de reportes móviles.
  2. Seleccionar y cargar diagramas desde MicroservicioBI.
  3. Interactuar táctilmente con gráficos adaptados.
- **Lista de Compra por Voz:**
  1. Activar función de voz.
  2. Dictar productos deseados.
  3. Procesar audio con IA, verificar stock y generar lista.
- **Funciones IA:**
  1. Acceder a análisis de IA (clasificación, predicción).
  2. Capturar datos necesarios y procesar con servicios remotos.
  3. Mostrar resultados adaptados para móvil.
**Postcondición:** Diagramas visualizados, listas de compra generadas y análisis de IA disponibles en móvil.
**Excepción:** Conexión inestable, reconocimiento de voz fallido, servicios no disponibles o datos insuficientes.
**Plataforma:** móvil
**Microservicio:** Core Service / ML Service / DL Service / MicroservicioBI

---

## 🔗 Matriz de Comunicación por Microservicio

| Microservicio | Puerto | Protocolo | Casos de Uso |
|---------------|--------|-----------|--------------|
| **Core Service** | 8080 | GraphQL | CU01 a CU05, CU13 |
| **ML Service** | 8081 | REST API | CU06 a CU08, CU13 |
| **DL Service** | 8082 | REST API | CU09, CU13 |
| **Frontend** | 5173 | HTTP/WS | Todos (consumidor) |
| **MicroservicioBI** | TBD | REST API | CU10 a CU11, CU13 |

---

## 📈 Estadísticas del Sistema

- **Total de Casos de Uso:** 13
- **Funcionalidades CRUD:** 5 (38%)
- **Funcionalidades IA:** 4 (31%)
- **Funcionalidades BI:** 2 (15%)
- **Funcionalidades Móviles:** 2 (15%)
- **Microservicios Integrados:** 5 (Core, ML, DL, Frontend, MicroservicioBI)
- **Reglas de Negocio Implementadas:** Control automático de inventario, IA integrada, BI avanzado

---

*Documento generado automáticamente basado en análisis del código fuente - Fecha: Noviembre 2025*</content>
<parameter name="filePath">/home/ubuntu/proyectos/proyecto-parcial2-sw2/CASOS_USO_COMPLETOS.md