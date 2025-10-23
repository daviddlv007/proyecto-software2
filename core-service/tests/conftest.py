"""
Configuración global de pytest para los tests de la API GraphQL
Define fixtures reutilizables y configuración común
"""

import pytest
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from typing import Dict, Any

# URL de la API
API_URL = "http://localhost:8080/graphql"


@pytest.fixture(scope="session")
def gql_client():
    """
    Cliente GraphQL para toda la sesión de tests
    Se conecta una sola vez y valida el schema automáticamente
    """
    transport = RequestsHTTPTransport(
        url=API_URL,
        verify=True,
        retries=3,
    )
    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,  # Valida contra el schema!
        execute_timeout=10
    )
    return client


@pytest.fixture
def categoria_test(gql_client):
    """
    Fixture que crea una categoría de prueba y la limpia después
    """
    # Setup: Crear categoría
    mutation = gql("""
        mutation {
          createCategoria(input: {
            nombre: "Test Categoria"
            descripcion: "Categoría para testing"
          }) {
            id
            nombre
            descripcion
          }
        }
    """)
    result = gql_client.execute(mutation)
    categoria = result['createCategoria']
    
    # Entregar la categoría al test
    yield categoria
    
    # Teardown: Limpiar después del test
    delete_mutation = gql(f"""
        mutation {{
          deleteCategoria(id: "{categoria['id']}")
        }}
    """)
    try:
        gql_client.execute(delete_mutation)
    except:
        pass  # Si ya fue eliminada, no importa


@pytest.fixture
def producto_test(gql_client, categoria_test):
    """
    Fixture que crea un producto de prueba vinculado a una categoría
    """
    # Setup: Crear producto
    mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Test Producto"
            descripcion: "Producto para testing"
            imagenUrl: "http://test.com/image.jpg"
            precio: 10.50
            stock: 100
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
            nombre
            precio
            stock
            categoria {{
              id
              nombre
            }}
          }}
        }}
    """)
    result = gql_client.execute(mutation)
    producto = result['createProducto']
    
    yield producto
    
    # Teardown
    delete_mutation = gql(f"""
        mutation {{
          deleteProducto(id: "{producto['id']}")
        }}
    """)
    try:
        gql_client.execute(delete_mutation)
    except:
        pass


@pytest.fixture
def cliente_test(gql_client):
    """
    Fixture que crea un cliente de prueba
    """
    mutation = gql("""
        mutation {
          createCliente(input: {
            nombre: "Test Cliente"
            correo: "test@example.com"
            telefono: "555-0000"
          }) {
            id
            nombre
            correo
            telefono
          }
        }
    """)
    result = gql_client.execute(mutation)
    cliente = result['createCliente']
    
    yield cliente
    
    delete_mutation = gql(f"""
        mutation {{
          deleteCliente(id: "{cliente['id']}")
        }}
    """)
    try:
        gql_client.execute(delete_mutation)
    except:
        pass


@pytest.fixture
def usuario_test(gql_client):
    """
    Fixture que crea un usuario de prueba
    """
    mutation = gql("""
        mutation {
          createUsuario(input: {
            nombre: "Test Usuario"
            correo: "test.user@example.com"
            contrasena: "testpass123"
          }) {
            id
            nombre
            correo
          }
        }
    """)
    result = gql_client.execute(mutation)
    usuario = result['createUsuario']
    
    yield usuario
    
    delete_mutation = gql(f"""
        mutation {{
          deleteUsuario(id: "{usuario['id']}")
        }}
    """)
    try:
        gql_client.execute(delete_mutation)
    except:
        pass


# Hooks de pytest para reportes personalizados
def pytest_configure(config):
    """Configuración inicial de pytest"""
    config.addinivalue_line(
        "markers", "smoke: Pruebas smoke básicas de la API"
    )
    config.addinivalue_line(
        "markers", "integration: Pruebas de integración completas"
    )
    config.addinivalue_line(
        "markers", "slow: Pruebas que tardan más tiempo"
    )


def pytest_html_report_title(report):
    """Título del reporte HTML"""
    report.title = "Reporte de Tests - API Supermercado GraphQL"
