"""
Tests para las operaciones CRUD de Categorías
"""

import pytest
from gql import gql


@pytest.mark.smoke
def test_crear_categoria(gql_client):
    """Test: Crear una nueva categoría"""
    mutation = gql("""
        mutation {
          createCategoria(input: {
            nombre: "Bebidas"
            descripcion: "Categoría de bebidas"
          }) {
            id
            nombre
            descripcion
          }
        }
    """)
    
    result = gql_client.execute(mutation)
    categoria = result['createCategoria']
    
    assert categoria['id'] is not None
    assert categoria['nombre'] == "Bebidas"
    assert categoria['descripcion'] == "Categoría de bebidas"
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteCategoria(id: "{categoria["id"]}") }}')
    gql_client.execute(cleanup)


@pytest.mark.smoke
def test_listar_categorias(gql_client, categoria_test):
    """Test: Listar todas las categorías"""
    query = gql("""
        query {
          categorias {
            id
            nombre
            descripcion
          }
        }
    """)
    
    result = gql_client.execute(query)
    categorias = result['categorias']
    
    assert isinstance(categorias, list)
    assert len(categorias) > 0
    
    # Verificar que nuestra categoría de test está en la lista
    ids = [cat['id'] for cat in categorias]
    assert categoria_test['id'] in ids


def test_actualizar_categoria(gql_client, categoria_test):
    """Test: Actualizar una categoría existente"""
    mutation = gql(f"""
        mutation {{
          updateCategoria(id: "{categoria_test['id']}", input: {{
            nombre: "Bebidas Actualizado"
            descripcion: "Nueva descripción"
          }}) {{
            id
            nombre
            descripcion
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    categoria = result['updateCategoria']
    
    assert categoria['id'] == categoria_test['id']
    assert categoria['nombre'] == "Bebidas Actualizado"
    assert categoria['descripcion'] == "Nueva descripción"


def test_eliminar_categoria(gql_client):
    """Test: Eliminar una categoría"""
    # Primero crear una
    create_mutation = gql("""
        mutation {
          createCategoria(input: {
            nombre: "Temporal"
            descripcion: "Para eliminar"
          }) {
            id
            nombre
          }
        }
    """)
    result = gql_client.execute(create_mutation)
    categoria_id = result['createCategoria']['id']
    
    # Ahora eliminarla
    delete_mutation = gql(f"""
        mutation {{
          deleteCategoria(id: "{categoria_id}")
        }}
    """)
    result = gql_client.execute(delete_mutation)
    
    assert result['deleteCategoria'] == True


def test_categoria_sin_descripcion(gql_client):
    """Test: Crear categoría sin descripción (campo opcional)"""
    mutation = gql("""
        mutation {
          createCategoria(input: {
            nombre: "Sin Descripcion"
          }) {
            id
            nombre
            descripcion
          }
        }
    """)
    
    result = gql_client.execute(mutation)
    categoria = result['createCategoria']
    
    assert categoria['nombre'] == "Sin Descripcion"
    assert categoria['descripcion'] is None
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteCategoria(id: "{categoria["id"]}") }}')
    gql_client.execute(cleanup)
