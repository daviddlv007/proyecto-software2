"""
Tests para las operaciones CRUD de Productos
"""

import pytest
from gql import gql


@pytest.mark.smoke
def test_crear_producto(gql_client, categoria_test):
    """Test: Crear un nuevo producto"""
    mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Coca Cola"
            descripcion: "Bebida gaseosa 2L"
            imagenUrl: "http://example.com/coca.jpg"
            precio: 5.50
            stock: 50
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
            nombre
            descripcion
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
    
    assert producto['id'] is not None
    assert producto['nombre'] == "Coca Cola"
    assert producto['precio'] == 5.50
    assert producto['stock'] == 50
    assert producto['categoria']['id'] == categoria_test['id']
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteProducto(id: "{producto["id"]}") }}')
    gql_client.execute(cleanup)


@pytest.mark.smoke
def test_listar_productos(gql_client, producto_test):
    """Test: Listar todos los productos"""
    query = gql("""
        query {
          productos {
            id
            nombre
            precio
            stock
            categoria {
              nombre
            }
          }
        }
    """)
    
    result = gql_client.execute(query)
    productos = result['productos']
    
    assert isinstance(productos, list)
    assert len(productos) > 0
    
    # Verificar que nuestro producto de test está en la lista
    ids = [prod['id'] for prod in productos]
    assert producto_test['id'] in ids


def test_actualizar_producto(gql_client, producto_test, categoria_test):
    """Test: Actualizar un producto existente"""
    mutation = gql(f"""
        mutation {{
          updateProducto(id: "{producto_test['id']}", input: {{
            nombre: "Coca Cola 3L"
            descripcion: "Versión grande"
            imagenUrl: "http://example.com/coca3l.jpg"
            precio: 7.50
            stock: 75
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
            nombre
            precio
            stock
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    producto = result['updateProducto']
    
    assert producto['id'] == producto_test['id']
    assert producto['nombre'] == "Coca Cola 3L"
    assert producto['precio'] == 7.50
    assert producto['stock'] == 75


def test_eliminar_producto(gql_client, categoria_test):
    """Test: Eliminar un producto"""
    # Crear producto
    create_mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Temporal"
            precio: 1.0
            stock: 1
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
          }}
        }}
    """)
    result = gql_client.execute(create_mutation)
    producto_id = result['createProducto']['id']
    
    # Eliminarlo
    delete_mutation = gql(f"""
        mutation {{
          deleteProducto(id: "{producto_id}")
        }}
    """)
    result = gql_client.execute(delete_mutation)
    
    assert result['deleteProducto'] == True


def test_producto_con_relacion_categoria(gql_client, producto_test, categoria_test):
    """Test: Verificar que la relación con categoría funciona correctamente"""
    query = gql(f"""
        query {{
          productos {{
            id
            nombre
            categoria {{
              id
              nombre
              descripcion
            }}
          }}
        }}
    """)
    
    result = gql_client.execute(query)
    productos = result['productos']
    
    # Buscar nuestro producto
    producto = next((p for p in productos if p['id'] == producto_test['id']), None)
    
    assert producto is not None
    assert producto['categoria']['id'] == categoria_test['id']
    assert producto['categoria']['nombre'] == categoria_test['nombre']


@pytest.mark.parametrize("precio,stock", [
    (0.01, 1),      # Mínimos válidos
    (999.99, 9999), # Máximos razonables
    (5.50, 0),      # Stock en 0 es válido
])
def test_producto_valores_limite(gql_client, categoria_test, precio, stock):
    """Test: Crear productos con valores límite"""
    mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Test Limite"
            precio: {precio}
            stock: {stock}
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
            precio
            stock
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    producto = result['createProducto']
    
    assert producto['precio'] == precio
    assert producto['stock'] == stock
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteProducto(id: "{producto["id"]}") }}')
    gql_client.execute(cleanup)
