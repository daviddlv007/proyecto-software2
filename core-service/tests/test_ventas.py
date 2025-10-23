"""
Tests para las operaciones complejas de Ventas
Incluye pruebas de transacciones con múltiples detalles
"""

import pytest
from gql import gql


@pytest.mark.smoke
@pytest.mark.integration
def test_crear_venta_completa(gql_client, cliente_test, producto_test):
    """Test: Crear una venta completa con detalles"""
    mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 5
                precioUnitario: 10.50
              }}
            ]
          }}) {{
            id
            fecha
            total
            cliente {{
              id
              nombre
            }}
            detalles {{
              id
              producto {{
                id
                nombre
              }}
              cantidad
              precioUnitario
              subtotal
            }}
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    venta = result['createVenta']
    
    assert venta['id'] is not None
    assert venta['fecha'] == "2025-10-23T00:00"
    assert venta['total'] == 52.50  # 5 * 10.50
    assert venta['cliente']['id'] == cliente_test['id']
    assert len(venta['detalles']) == 1
    assert venta['detalles'][0]['cantidad'] == 5
    assert venta['detalles'][0]['precioUnitario'] == 10.50
    assert venta['detalles'][0]['subtotal'] == 52.50
    
    # Limpiar
    cleanup = gql(f'mutation {{ deleteVenta(id: "{venta["id"]}") }}')
    gql_client.execute(cleanup)


@pytest.mark.integration
def test_crear_venta_multiples_productos(gql_client, cliente_test, categoria_test):
    """Test: Crear venta con múltiples productos"""
    # Primero crear dos productos
    prod1_mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Producto 1"
            precio: 5.0
            stock: 100
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
          }}
        }}
    """)
    prod1_result = gql_client.execute(prod1_mutation)
    prod1_id = prod1_result['createProducto']['id']
    
    prod2_mutation = gql(f"""
        mutation {{
          createProducto(input: {{
            nombre: "Producto 2"
            precio: 3.0
            stock: 100
            categoriaId: "{categoria_test['id']}"
          }}) {{
            id
          }}
        }}
    """)
    prod2_result = gql_client.execute(prod2_mutation)
    prod2_id = prod2_result['createProducto']['id']
    
    # Crear venta con ambos productos
    venta_mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{prod1_id}"
                cantidad: 2
                precioUnitario: 5.0
              }},
              {{
                productoId: "{prod2_id}"
                cantidad: 3
                precioUnitario: 3.0
              }}
            ]
          }}) {{
            id
            total
            detalles {{
              cantidad
              precioUnitario
              subtotal
            }}
          }}
        }}
    """)
    
    result = gql_client.execute(venta_mutation)
    venta = result['createVenta']
    
    assert len(venta['detalles']) == 2
    assert venta['total'] == 19.0  # (2*5.0) + (3*3.0) = 10 + 9 = 19
    
    # Limpiar
    gql_client.execute(gql(f'mutation {{ deleteVenta(id: "{venta["id"]}") }}'))
    gql_client.execute(gql(f'mutation {{ deleteProducto(id: "{prod1_id}") }}'))
    gql_client.execute(gql(f'mutation {{ deleteProducto(id: "{prod2_id}") }}'))


@pytest.mark.smoke
def test_listar_ventas(gql_client, cliente_test, producto_test):
    """Test: Listar todas las ventas"""
    # Crear una venta primero
    create_mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 1
                precioUnitario: 10.50
              }}
            ]
          }}) {{
            id
          }}
        }}
    """)
    create_result = gql_client.execute(create_mutation)
    venta_id = create_result['createVenta']['id']
    
    # Listar
    query = gql("""
        query {
          ventas {
            id
            fecha
            total
            cliente {
              nombre
            }
            detalles {
              producto {
                nombre
              }
              cantidad
              precioUnitario
              subtotal
            }
          }
        }
    """)
    
    result = gql_client.execute(query)
    ventas = result['ventas']
    
    assert isinstance(ventas, list)
    assert len(ventas) > 0
    
    ids = [v['id'] for v in ventas]
    assert venta_id in ids
    
    # Limpiar
    gql_client.execute(gql(f'mutation {{ deleteVenta(id: "{venta_id}") }}'))


@pytest.mark.integration
def test_actualizar_venta(gql_client, cliente_test, producto_test):
    """Test: Actualizar una venta existente (cambiar cantidades)"""
    # Crear venta
    create_mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 2
                precioUnitario: 10.50
              }}
            ]
          }}) {{
            id
            total
          }}
        }}
    """)
    create_result = gql_client.execute(create_mutation)
    venta_id = create_result['createVenta']['id']
    total_original = create_result['createVenta']['total']
    
    assert total_original == 21.0  # 2 * 10.50
    
    # Actualizar (cambiar cantidad a 5)
    update_mutation = gql(f"""
        mutation {{
          updateVenta(id: "{venta_id}", input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 5
                precioUnitario: 10.50
              }}
            ]
          }}) {{
            id
            total
            detalles {{
              cantidad
              precioUnitario
              subtotal
            }}
          }}
        }}
    """)
    
    update_result = gql_client.execute(update_mutation)
    venta = update_result['updateVenta']
    
    assert venta['id'] == venta_id
    assert venta['total'] == 52.50  # 5 * 10.50
    assert venta['detalles'][0]['cantidad'] == 5
    assert venta['detalles'][0]['subtotal'] == 52.50
    
    # Limpiar
    gql_client.execute(gql(f'mutation {{ deleteVenta(id: "{venta_id}") }}'))


def test_eliminar_venta(gql_client, cliente_test, producto_test):
    """Test: Eliminar una venta"""
    # Crear
    create_mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 1
                precioUnitario: 10.50
              }}
            ]
          }}) {{
            id
          }}
        }}
    """)
    result = gql_client.execute(create_mutation)
    venta_id = result['createVenta']['id']
    
    # Eliminar
    delete_mutation = gql(f"""
        mutation {{
          deleteVenta(id: "{venta_id}")
        }}
    """)
    result = gql_client.execute(delete_mutation)
    
    assert result['deleteVenta'] == True


@pytest.mark.slow
@pytest.mark.integration
def test_calculo_total_automatico(gql_client, cliente_test, producto_test):
    """Test: Verificar que el total se calcula automáticamente"""
    mutation = gql(f"""
        mutation {{
          createVenta(input: {{
            clienteId: "{cliente_test['id']}"
            fecha: "2025-10-23"
            detalles: [
              {{
                productoId: "{producto_test['id']}"
                cantidad: 7
                precioUnitario: 3.25
              }}
            ]
          }}) {{
            id
            total
            detalles {{
              subtotal
            }}
          }}
        }}
    """)
    
    result = gql_client.execute(mutation)
    venta = result['createVenta']
    
    # Verificar cálculo: 7 * 3.25 = 22.75
    assert venta['total'] == 22.75
    assert venta['detalles'][0]['subtotal'] == 22.75
    
    # Limpiar
    gql_client.execute(gql(f'mutation {{ deleteVenta(id: "{venta["id"]}") }}'))
