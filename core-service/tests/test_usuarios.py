"""
Tests para las operaciones CRUD de Usuarios
"""

import pytest
from gql import gql


@pytest.mark.smoke
def test_crear_usuario(gql_client):
    """Test: Crear un nuevo usuario"""
    mutation = gql("""
        mutation {
          createUsuario(input: {
            nombre: "Admin Test"
            correo: "admin@example.com"
            contrasena: "password123"
          }) {
            id
            nombre
            correo
          }
        }
    """)
    
    result = gql_client.execute(mutation)
    usuario = result['createUsuario']
    
    assert usuario['id'] is not None
    assert usuario['nombre'] == "Admin Test"
    assert usuario['correo'] == "admin@example.com"
    # Nota: La contraseña no se devuelve por seguridad
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteUsuario(id: "{usuario["id"]}") }}')
    gql_client.execute(cleanup)


@pytest.mark.smoke
def test_listar_usuarios(gql_client, usuario_test):
    """Test: Listar todos los usuarios"""
    query = gql("""
        query {
          usuarios {
            id
            nombre
            correo
          }
        }
    """)
    
    result = gql_client.execute(query)
    usuarios = result['usuarios']
    
    assert isinstance(usuarios, list)
    assert len(usuarios) > 0
    
    ids = [u['id'] for u in usuarios]
    assert usuario_test['id'] in ids


def test_actualizar_usuario(gql_client, usuario_test):
    """Test: Actualizar un usuario existente"""
    mutation = gql(f"""
        mutation {{
          updateUsuario(id: "{usuario_test['id']}", input: {{
            nombre: "Admin Test Updated"
            correo: "admin.new@example.com"
            contrasena: "newpassword456"
          }}) {{
            id
            nombre
            correo
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    usuario = result['updateUsuario']
    
    assert usuario['id'] == usuario_test['id']
    assert usuario['nombre'] == "Admin Test Updated"
    assert usuario['correo'] == "admin.new@example.com"


def test_eliminar_usuario(gql_client):
    """Test: Eliminar un usuario"""
    # Crear
    create_mutation = gql("""
        mutation {
          createUsuario(input: {
            nombre: "Temporal"
            correo: "temp@example.com"
            contrasena: "temp123"
          }) {
            id
          }
        }
    """)
    result = gql_client.execute(create_mutation)
    usuario_id = result['createUsuario']['id']
    
    # Eliminar
    delete_mutation = gql(f"""
        mutation {{
          deleteUsuario(id: "{usuario_id}")
        }}
    """)
    result = gql_client.execute(delete_mutation)
    
    assert result['deleteUsuario'] == True
