import requests

URL = "http://localhost:8080/graphql"  # Ajusta según tu servidor

# Datos de prueba para cada entidad
entities = {
    "Categoria": {"nombre": "test_string", "descripcion": "test_string"},
    "Producto": {"nombre": "test_string", "descripcion": "test_string", "precio": 3.5, "stock": 10},
    "Cliente": {"nombre": "test_string", "correo": "test@mail.com", "telefono": "123456"},
    "Usuario": {"nombre": "test_string", "correo": "test@mail.com", "contrasena": "123456"},
    "Venta": {"fecha": "2025-10-15", "total": 100.0},
    "DetalleVenta": {"cantidad": 2, "precioUnitario": 50.0},
}

# Guardamos IDs para dependencias
ids = {}

def run_query(query, variables=None):
    payload = {"query": query, "variables": variables}
    r = requests.post(URL, json=payload)
    res = r.json()
    if "errors" in res:
        print("Error:", res["errors"])
    return res.get("data")

def test_categoria():
    print("\n--- Categoria ---")
    # Create
    q = """
    mutation($nombre: String!, $descripcion: String) {
      createCategoria(nombre: $nombre, descripcion: $descripcion) { id nombre descripcion }
    }
    """
    data = run_query(q, entities["Categoria"])
    ids["Categoria"] = data["createCategoria"]["id"]
    print("Create:", data["createCategoria"])
    
    # Read
    q = "{ allCategorias { id nombre descripcion } }"
    data = run_query(q)
    print("Read:", data["allCategorias"])

def test_producto():
    print("\n--- Producto ---")
    if "Categoria" not in ids:
        print("⚠ No hay Categoria creada, saltando Producto")
        return
    
    q = """
    mutation($nombre: String!, $descripcion: String, $precio: Float!, $stock: Int, $categoriaId: ID!) {
      createProducto(nombre: $nombre, descripcion: $descripcion, precio: $precio, stock: $stock, categoriaId: $categoriaId) {
        id nombre precio stock categoria { id nombre }
      }
    }
    """
    variables = entities["Producto"].copy()
    variables["categoriaId"] = ids["Categoria"]
    data = run_query(q, variables)
    ids["Producto"] = data["createProducto"]["id"]
    print("Create:", data["createProducto"])
    
    # Read
    q = "{ allProductos { id nombre precio stock categoria { id nombre } } }"
    data = run_query(q)
    print("Read:", data["allProductos"])

def test_cliente():
    print("\n--- Cliente ---")
    q = """
    mutation($nombre: String!, $correo: String!, $telefono: String) {
      createCliente(nombre: $nombre, correo: $correo, telefono: $telefono) { id nombre correo telefono }
    }
    """
    data = run_query(q, entities["Cliente"])
    ids["Cliente"] = data["createCliente"]["id"]
    print("Create:", data["createCliente"])
    
    q = "{ allClientes { id nombre correo telefono } }"
    data = run_query(q)
    print("Read:", data["allClientes"])

def test_venta():
    print("\n--- Venta ---")
    if "Cliente" not in ids:
        print("⚠ No hay Cliente creada, saltando Venta")
        return
    
    q = """
    mutation($clienteId: ID!, $fecha: String, $total: Float!) {
      createVenta(clienteId: $clienteId, fecha: $fecha, total: $total) { id fecha total cliente { id nombre } }
    }
    """
    variables = entities["Venta"].copy()
    variables["clienteId"] = ids["Cliente"]
    data = run_query(q, variables)
    ids["Venta"] = data["createVenta"]["id"]
    print("Create:", data["createVenta"])

def test_detalleventa():
    print("\n--- DetalleVenta ---")
    if "Venta" not in ids or "Producto" not in ids:
        print("⚠ No hay Venta o Producto creada, saltando DetalleVenta")
        return
    
    q = """
    mutation($ventaId: ID!, $productoId: ID!, $cantidad: Int!, $precioUnitario: Float!) {
      createDetalleVenta(ventaId: $ventaId, productoId: $productoId, cantidad: $cantidad, precioUnitario: $precioUnitario) {
        id cantidad precioUnitario venta { id } producto { id nombre }
      }
    }
    """
    variables = entities["DetalleVenta"].copy()
    variables["ventaId"] = ids["Venta"]
    variables["productoId"] = ids["Producto"]
    data = run_query(q, variables)
    ids["DetalleVenta"] = data["createDetalleVenta"]["id"]
    print("Create:", data["createDetalleVenta"])

# Ejecutar todas las pruebas en orden
test_categoria()
test_producto()
test_cliente()
test_venta()
test_detalleventa()
