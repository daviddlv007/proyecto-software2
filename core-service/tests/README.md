# Tests de la API GraphQL con Pytest

Tests profesionales para la API GraphQL del sistema de gestión de supermercado usando **Pytest + GQL**.

## 📦 Instalación

```bash
cd core-service/tests
./run_tests.sh  # Instala automáticamente si es necesario
```

O manualmente:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Ejecución Rápida

### Con el script (recomendado)
```bash
./run_tests.sh                    # Ejecutar todos con reporte HTML
./run_tests.sh -m smoke          # Solo tests rápidos
./run_tests.sh test_ventas.py    # Solo tests de ventas
./run_tests.sh -k crear          # Tests que contengan "crear"
```

### Manual con pytest
```bash
source venv/bin/activate
pytest -v
```

### Con reporte HTML detallado
```bash
pytest --html=report.html --self-contained-html
```

### Con cobertura de código
```bash
pytest --cov --cov-report=html
```

### Solo tests smoke (rápidos)
```bash
pytest -m smoke
```

### Solo tests de integración
```bash
pytest -m integration
```

### Tests específicos
```bash
pytest test_categorias.py                    # Solo categorías
pytest test_ventas.py::test_crear_venta_completa  # Un test específico
```

### Verbose (más detalles)
```bash
pytest -v
```

### Ver print statements
```bash
pytest -s
```

## 📁 Estructura de Archivos

```
tests/
├── conftest.py              # Configuración global y fixtures
├── requirements.txt         # Dependencias
├── run_tests.sh            # ⭐ Script ejecutor con auto-setup
├── test_categorias.py       # Tests de categorías
├── test_productos.py        # Tests de productos
├── test_clientes.py         # Tests de clientes
├── test_usuarios.py         # Tests de usuarios
├── test_ventas.py          # Tests de ventas (integración)
├── test_complete_api.py    # Script original (legacy)
├── README.md               # Esta documentación
└── COMPARACION.md          # Comparación vs script original
```

## 🏷️ Marks (Etiquetas)

Los tests están marcados con etiquetas para ejecutarlos selectivamente:

- `@pytest.mark.smoke` - Tests básicos y rápidos
- `@pytest.mark.integration` - Tests de integración complejos
- `@pytest.mark.slow` - Tests que tardan más tiempo

## 🔧 Fixtures Disponibles

Las fixtures se definen en `conftest.py` y se reutilizan en todos los tests:

### `gql_client`
Cliente GraphQL configurado y validado contra el schema.

```python
def test_algo(gql_client):
    query = gql("query { categorias { id } }")
    result = gql_client.execute(query)
```

### `categoria_test`
Crea una categoría de prueba y la limpia automáticamente.

```python
def test_algo(categoria_test):
    assert categoria_test['id'] is not None
    # No necesitas limpiarla, se hace automáticamente
```

### `producto_test`
Crea un producto de prueba vinculado a una categoría.

```python
def test_algo(producto_test, categoria_test):
    assert producto_test['categoria']['id'] == categoria_test['id']
```

### `cliente_test`
Crea un cliente de prueba.

### `usuario_test`
Crea un usuario de prueba.

## 📊 Reportes

### Reporte en Terminal
```bash
pytest -v
```

Salida:
```
test_categorias.py::test_crear_categoria PASSED                    [ 10%]
test_categorias.py::test_listar_categorias PASSED                  [ 20%]
test_categorias.py::test_actualizar_categoria PASSED               [ 30%]
...
======================== 25 passed in 5.23s ==========================
```

### Reporte HTML
```bash
pytest --html=report.html --self-contained-html
```

Genera un archivo `report.html` con:
- ✅ Tests pasados/fallidos
- ⏱️ Tiempo de ejecución
- 📋 Logs detallados
- 📊 Gráficas

### Cobertura de Código
```bash
pytest --cov=. --cov-report=html
```

Genera `htmlcov/index.html` con:
- % de cobertura por archivo
- Líneas cubiertas/no cubiertas
- Ramas condicionales

## 🎯 Ejemplos de Uso

### Test Simple
```python
def test_crear_categoria(gql_client):
    mutation = gql("""
        mutation {
          createCategoria(input: {
            nombre: "Test"
            descripcion: "Desc"
          }) {
            id
            nombre
          }
        }
    """)
    
    result = gql_client.execute(mutation)
    assert result['createCategoria']['nombre'] == "Test"
```

### Test con Fixture
```python
def test_producto_con_categoria(producto_test, categoria_test):
    # producto_test ya viene creado y vinculado a categoria_test
    assert producto_test['categoria']['id'] == categoria_test['id']
```

### Test Parametrizado
```python
@pytest.mark.parametrize("precio,stock", [
    (0.01, 1),
    (999.99, 9999),
])
def test_valores_limite(gql_client, precio, stock):
    # Se ejecuta una vez por cada par de valores
    pass
```

### Test de Integración
```python
@pytest.mark.integration
def test_venta_completa(gql_client, cliente_test, producto_test):
    # Test complejo que usa múltiples entidades
    pass
```

## 🐛 Debugging

### Ver detalles de un test fallido
```bash
pytest -vv --tb=long
```

### Ejecutar solo el test que falló
```bash
pytest --lf  # last-failed
```

### Ejecutar hasta que falle
```bash
pytest -x  # stop on first failure
```

### Modo debug interactivo
```bash
pytest --pdb
```

## 🔄 Integración con CI/CD

### GitHub Actions
```yaml
- name: Run tests
  run: |
    cd core-service/tests
    pip install -r requirements.txt
    pytest --html=report.html --self-contained-html
    
- name: Upload test report
  uses: actions/upload-artifact@v2
  if: always()
  with:
    name: test-report
    path: core-service/tests/report.html
```

### GitLab CI
```yaml
test:
  script:
    - cd core-service/tests
    - pip install -r requirements.txt
    - pytest --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: core-service/tests/report.xml
```

## 📈 Comparación de Rendimiento

| Métrica | Script Original | Pytest + GQL |
|---------|----------------|--------------|
| Tiempo ejecución | ~15s | **5.83s** ⚡ |
| Tests ejecutados | 20 | **33** |
| Setup/Teardown | Manual | Automático |
| Validación schema | No | Sí |
| Reportes | Terminal | HTML + Terminal |
| Reutilización código | Baja | Alta |

📊 **Ver análisis completo en [COMPARACION.md](COMPARACION.md)**

## 🎓 Aprende Más

- [Pytest Docs](https://docs.pytest.org/)
- [GQL Python](https://gql.readthedocs.io/)
- [Pytest Markers](https://docs.pytest.org/en/stable/mark.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)

## ⚙️ Configuración Avanzada

### pytest.ini (opcional)
```ini
[pytest]
addopts = -v --tb=short
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: Quick smoke tests
    integration: Integration tests
    slow: Slow tests
```

## 🆘 Solución de Problemas

### Error: "No module named 'gql'"
```bash
pip install -r requirements.txt
```

### Error: "Schema validation failed"
Asegúrate de que el backend esté corriendo en `http://localhost:8080`

### Tests muy lentos
Ejecuta solo tests smoke:
```bash
pytest -m smoke
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que el backend esté corriendo
2. Revisa los logs con `pytest -vv`
3. Ejecuta un test individual para debugging
4. Consulta la documentación de Pytest
