"""
Tests para las operaciones CRUD de Clientes
"""

import pytest
from gql import gql


@pytest.mark.smoke
def test_crear_cliente(gql_client):
    """Test: Crear un nuevo cliente"""
    mutation = gql("""
        mutation {
          createCliente(input: {
            nombre: "Juan Pérez"
            correo: "juan@example.com"
            telefono: "555-1234"
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
    
    assert cliente['id'] is not None
    assert cliente['nombre'] == "Juan Pérez"
    assert cliente['correo'] == "juan@example.com"
    assert cliente['telefono'] == "555-1234"
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteCliente(id: "{cliente["id"]}") }}')
    gql_client.execute(cleanup)


@pytest.mark.smoke
def test_listar_clientes(gql_client, cliente_test):
    """Test: Listar todos los clientes"""
    query = gql("""
        query {
          clientes {
            id
            nombre
            correo
            telefono
          }
        }
    """)
    
    result = gql_client.execute(query)
    clientes = result['clientes']
    
    assert isinstance(clientes, list)
    assert len(clientes) > 0
    
    ids = [c['id'] for c in clientes]
    assert cliente_test['id'] in ids


def test_actualizar_cliente(gql_client, cliente_test):
    """Test: Actualizar un cliente existente"""
    mutation = gql(f"""
        mutation {{
          updateCliente(id: "{cliente_test['id']}", input: {{
            nombre: "Juan Pérez Actualizado"
            correo: "juan.nuevo@example.com"
            telefono: "555-9999"
          }}) {{
            id
            nombre
            correo
            telefono
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    cliente = result['updateCliente']
    
    assert cliente['id'] == cliente_test['id']
    assert cliente['nombre'] == "Juan Pérez Actualizado"
    assert cliente['correo'] == "juan.nuevo@example.com"
    assert cliente['telefono'] == "555-9999"


def test_eliminar_cliente(gql_client):
    """Test: Eliminar un cliente"""
    # Crear
    create_mutation = gql("""
        mutation {
          createCliente(input: {
            nombre: "Temporal"
            correo: "temp@example.com"
            telefono: "000-0000"
          }) {
            id
          }
        }
    """)
    result = gql_client.execute(create_mutation)
    cliente_id = result['createCliente']['id']
    
    # Eliminar
    delete_mutation = gql(f"""
        mutation {{
          deleteCliente(id: "{cliente_id}")
        }}
    """)
    result = gql_client.execute(delete_mutation)
    
    assert result['deleteCliente'] == True
