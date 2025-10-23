#!/usr/bin/env python3
"""
Script para generar datos REALISTAS para ML/DL + Reportes
- Datos coherentes y lógicos para gráficas
- Compatibles con modelos pre-entrenados
- Suficientes para demostraciones convincentes
"""

import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

# Configuración
GRAPHQL_URL = "http://localhost:8080/graphql"
VERBOSE = True

# =======================================
# DATOS REALISTAS DE SUPERMERCADO
# =======================================

# Categorías con productos reales y precios lógicos
CATEGORIAS_PRODUCTOS = {
    "Bebidas": [
        {"nombre": "Coca-Cola 2L", "precio": 2.50, "stock_promedio": 80},
        {"nombre": "Sprite 2L", "precio": 2.50, "stock_promedio": 70},
        {"nombre": "Fanta 2L", "precio": 2.50, "stock_promedio": 60},
        {"nombre": "Agua Mineral 1L", "precio": 0.80, "stock_promedio": 150},
        {"nombre": "Jugo de Naranja 1L", "precio": 3.20, "stock_promedio": 50},
        {"nombre": "Cerveza Pilsener 355ml", "precio": 1.00, "stock_promedio": 120},
        {"nombre": "Energizante Red Bull", "precio": 1.80, "stock_promedio": 40},
    ],
    "Lácteos": [
        {"nombre": "Leche Entera 1L", "precio": 1.20, "stock_promedio": 100},
        {"nombre": "Yogurt Natural 1L", "precio": 2.80, "stock_promedio": 60},
        {"nombre": "Queso Fresco 500g", "precio": 4.50, "stock_promedio": 40},
        {"nombre": "Mantequilla 250g", "precio": 2.30, "stock_promedio": 50},
        {"nombre": "Yogurt Griego", "precio": 3.50, "stock_promedio": 35},
    ],
    "Panadería": [
        {"nombre": "Pan Blanco", "precio": 0.25, "stock_promedio": 200},
        {"nombre": "Pan Integral", "precio": 0.35, "stock_promedio": 150},
        {"nombre": "Galletas Saladas", "precio": 1.50, "stock_promedio": 80},
        {"nombre": "Galletas Dulces", "precio": 1.80, "stock_promedio": 75},
        {"nombre": "Pastel Chocolate", "precio": 8.50, "stock_promedio": 15},
        {"nombre": "Croissant", "precio": 1.20, "stock_promedio": 40},
    ],
    "Carnes": [
        {"nombre": "Pollo Entero kg", "precio": 3.50, "stock_promedio": 60},
        {"nombre": "Carne de Res kg", "precio": 8.50, "stock_promedio": 40},
        {"nombre": "Cerdo Chuleta kg", "precio": 6.20, "stock_promedio": 35},
        {"nombre": "Pescado Tilapia kg", "precio": 5.80, "stock_promedio": 30},
        {"nombre": "Salchicha Pack 500g", "precio": 3.20, "stock_promedio": 70},
    ],
    "Frutas": [
        {"nombre": "Manzana kg", "precio": 1.50, "stock_promedio": 100},
        {"nombre": "Plátano kg", "precio": 0.80, "stock_promedio": 120},
        {"nombre": "Naranja kg", "precio": 1.20, "stock_promedio": 90},
        {"nombre": "Uva kg", "precio": 3.50, "stock_promedio": 50},
        {"nombre": "Sandía Unidad", "precio": 4.00, "stock_promedio": 25},
        {"nombre": "Piña Unidad", "precio": 2.50, "stock_promedio": 40},
    ],
    "Verduras": [
        {"nombre": "Tomate kg", "precio": 1.20, "stock_promedio": 80},
        {"nombre": "Cebolla kg", "precio": 0.90, "stock_promedio": 100},
        {"nombre": "Zanahoria kg", "precio": 0.70, "stock_promedio": 90},
        {"nombre": "Lechuga Unidad", "precio": 0.60, "stock_promedio": 70},
        {"nombre": "Brócoli kg", "precio": 1.80, "stock_promedio": 50},
        {"nombre": "Papa kg", "precio": 0.50, "stock_promedio": 150},
    ],
    "Limpieza": [
        {"nombre": "Detergente 1kg", "precio": 3.50, "stock_promedio": 60},
        {"nombre": "Jabón Líquido 500ml", "precio": 2.80, "stock_promedio": 70},
        {"nombre": "Papel Higiénico 4u", "precio": 2.20, "stock_promedio": 100},
        {"nombre": "Cloro 1L", "precio": 1.50, "stock_promedio": 80},
        {"nombre": "Esponja Pack 3u", "precio": 1.20, "stock_promedio": 90},
    ],
    "Snacks": [
        {"nombre": "Papas Fritas 150g", "precio": 1.50, "stock_promedio": 100},
        {"nombre": "Doritos 200g", "precio": 2.20, "stock_promedio": 85},
        {"nombre": "Chocolate Snickers", "precio": 0.80, "stock_promedio": 120},
        {"nombre": "Caramelos Bolsa", "precio": 0.50, "stock_promedio": 150},
        {"nombre": "Maní Salado 100g", "precio": 1.20, "stock_promedio": 70},
        {"nombre": "Chicles Pack", "precio": 0.30, "stock_promedio": 180},
    ],
}

# Perfiles de clientes realistas (para segmentación ML)
PERFILES_CLIENTES = [
    # VIP - Compran mucho, frecuentemente, ticket alto
    {"tipo": "VIP", "nombre": "María González", "correo": "maria.g@email.com", "telefono": "0991234567", 
     "frecuencia_compras": (3, 5), "ticket_promedio": (25, 50), "productos_favoritos": ["Carnes", "Lácteos", "Frutas"]},
    {"tipo": "VIP", "nombre": "Carlos Ruiz", "correo": "carlos.r@email.com", "telefono": "0991234568",
     "frecuencia_compras": (4, 6), "ticket_promedio": (30, 60), "productos_favoritos": ["Bebidas", "Carnes", "Snacks"]},
    {"tipo": "VIP", "nombre": "Ana Martínez", "correo": "ana.m@email.com", "telefono": "0991234569",
     "frecuencia_compras": (3, 5), "ticket_promedio": (28, 55), "productos_favoritos": ["Lácteos", "Panadería", "Frutas"]},
    
    # REGULARES - Compran moderadamente
    {"tipo": "REGULAR", "nombre": "Juan Pérez", "correo": "juan.p@email.com", "telefono": "0991234570",
     "frecuencia_compras": (2, 3), "ticket_promedio": (15, 30), "productos_favoritos": ["Bebidas", "Snacks", "Panadería"]},
    {"tipo": "REGULAR", "nombre": "Laura Sánchez", "correo": "laura.s@email.com", "telefono": "0991234571",
     "frecuencia_compras": (2, 4), "ticket_promedio": (12, 28), "productos_favoritos": ["Lácteos", "Verduras", "Frutas"]},
    {"tipo": "REGULAR", "nombre": "Pedro López", "correo": "pedro.l@email.com", "telefono": "0991234572",
     "frecuencia_compras": (1, 3), "ticket_promedio": (18, 32), "productos_favoritos": ["Carnes", "Bebidas", "Limpieza"]},
    {"tipo": "REGULAR", "nombre": "Sofía Torres", "correo": "sofia.t@email.com", "telefono": "0991234573",
     "frecuencia_compras": (2, 3), "ticket_promedio": (14, 26), "productos_favoritos": ["Panadería", "Lácteos", "Snacks"]},
    {"tipo": "REGULAR", "nombre": "Diego Morales", "correo": "diego.m@email.com", "telefono": "0991234574",
     "frecuencia_compras": (2, 4), "ticket_promedio": (16, 30), "productos_favoritos": ["Bebidas", "Carnes", "Frutas"]},
    {"tipo": "REGULAR", "nombre": "Carmen Vega", "correo": "carmen.v@email.com", "telefono": "0991234575",
     "frecuencia_compras": (1, 3), "ticket_promedio": (13, 25), "productos_favoritos": ["Verduras", "Frutas", "Lácteos"]},
    {"tipo": "REGULAR", "nombre": "Roberto Castro", "correo": "roberto.c@email.com", "telefono": "0991234576",
     "frecuencia_compras": (2, 3), "ticket_promedio": (17, 29), "productos_favoritos": ["Limpieza", "Bebidas", "Snacks"]},
    
    # OCASIONALES - Compran poco, esporádicamente
    {"tipo": "OCASIONAL", "nombre": "Elena Flores", "correo": "elena.f@email.com", "telefono": "0991234577",
     "frecuencia_compras": (1, 2), "ticket_promedio": (5, 15), "productos_favoritos": ["Snacks", "Bebidas"]},
    {"tipo": "OCASIONAL", "nombre": "Miguel Herrera", "correo": "miguel.h@email.com", "telefono": "0991234578",
     "frecuencia_compras": (1, 2), "ticket_promedio": (6, 12), "productos_favoritos": ["Panadería", "Bebidas"]},
    {"tipo": "OCASIONAL", "nombre": "Patricia Rojas", "correo": "patricia.r@email.com", "telefono": "0991234579",
     "frecuencia_compras": (1, 1), "ticket_promedio": (4, 10), "productos_favoritos": ["Snacks"]},
    {"tipo": "OCASIONAL", "nombre": "Fernando Silva", "correo": "fernando.s@email.com", "telefono": "0991234580",
     "frecuencia_compras": (1, 2), "ticket_promedio": (7, 14), "productos_favoritos": ["Bebidas", "Snacks"]},
    {"tipo": "OCASIONAL", "nombre": "Isabel Mendoza", "correo": "isabel.m@email.com", "telefono": "0991234581",
     "frecuencia_compras": (1, 2), "ticket_promedio": (5, 13), "productos_favoritos": ["Panadería", "Lácteos"]},
    {"tipo": "OCASIONAL", "nombre": "Andrés Vargas", "correo": "andres.v@email.com", "telefono": "0991234582",
     "frecuencia_compras": (1, 1), "ticket_promedio": (8, 15), "productos_favoritos": ["Limpieza", "Bebidas"]},
    
    # Más REGULARES para balance
    {"tipo": "REGULAR", "nombre": "Gabriela Ortiz", "correo": "gabriela.o@email.com", "telefono": "0991234583",
     "frecuencia_compras": (2, 3), "ticket_promedio": (15, 27), "productos_favoritos": ["Frutas", "Verduras", "Lácteos"]},
    {"tipo": "REGULAR", "nombre": "Ricardo Navarro", "correo": "ricardo.n@email.com", "telefono": "0991234584",
     "frecuencia_compras": (2, 4), "ticket_promedio": (16, 31), "productos_favoritos": ["Carnes", "Bebidas", "Limpieza"]},
    {"tipo": "REGULAR", "nombre": "Verónica Guzmán", "correo": "veronica.g@email.com", "telefono": "0991234585",
     "frecuencia_compras": (2, 3), "ticket_promedio": (14, 28), "productos_favoritos": ["Lácteos", "Panadería", "Snacks"]},
    {"tipo": "REGULAR", "nombre": "Javier Ramírez", "correo": "javier.r@email.com", "telefono": "0991234586",
     "frecuencia_compras": (1, 3), "ticket_promedio": (17, 30), "productos_favoritos": ["Bebidas", "Carnes", "Frutas"]},
    
    # Más OCASIONALES
    {"tipo": "OCASIONAL", "nombre": "Cristina Paredes", "correo": "cristina.p@email.com", "telefono": "0991234587",
     "frecuencia_compras": (1, 2), "ticket_promedio": (6, 14), "productos_favoritos": ["Snacks", "Bebidas"]},
    {"tipo": "OCASIONAL", "nombre": "Esteban Córdova", "correo": "esteban.c@email.com", "telefono": "0991234588",
     "frecuencia_compras": (1, 1), "ticket_promedio": (5, 11), "productos_favoritos": ["Panadería"]},
    {"tipo": "OCASIONAL", "nombre": "Daniela Moreno", "correo": "daniela.m@email.com", "telefono": "0991234589",
     "frecuencia_compras": (1, 2), "ticket_promedio": (7, 13), "productos_favoritos": ["Lácteos", "Snacks"]},
    
    # Un par más de VIP
    {"tipo": "VIP", "nombre": "Sergio Velasco", "correo": "sergio.v@email.com", "telefono": "0991234590",
     "frecuencia_compras": (4, 5), "ticket_promedio": (32, 58), "productos_favoritos": ["Carnes", "Bebidas", "Lácteos"]},
    {"tipo": "VIP", "nombre": "Mónica Salazar", "correo": "monica.s@email.com", "telefono": "0991234591",
     "frecuencia_compras": (3, 6), "ticket_promedio": (27, 52), "productos_favoritos": ["Frutas", "Verduras", "Carnes"]},
]

# =======================================
# FUNCIONES DE UTILIDAD
# =======================================

def ejecutar_graphql(query: str, variables: dict = None) -> dict:
    """Ejecuta query/mutation GraphQL"""
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if "errors" in result:
            print(f"❌ Error GraphQL: {result['errors']}")
            return None
            
        return result.get("data", {})
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def log(mensaje: str):
    """Log con timestamp"""
    if VERBOSE:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")

# =======================================
# GENERACIÓN DE DATOS
# =======================================

class GeneradorDatos:
    def __init__(self):
        self.categorias_ids = {}
        self.productos_ids = {}
        self.productos_por_categoria = {}
        self.clientes_ids = {}
        self.usuarios_ids = {}
        self.ventas_generadas = 0
        
    def generar_todo(self):
        """Pipeline completo de generación"""
        log("🚀 Iniciando generación de datos realistas para ML/DL/Reportes")
        
        self.crear_categorias()
        self.crear_productos()
        self.crear_usuarios()
        self.crear_clientes()
        self.crear_ventas_realistas()
        
        self.mostrar_resumen()
        log("✅ Generación completada exitosamente")
        
    def crear_categorias(self):
        """Crear categorías base"""
        log("📦 Creando categorías...")
        
        for nombre_cat in CATEGORIAS_PRODUCTOS.keys():
            mutation = """
                mutation($input: CategoriaInput!) {
                    createCategoria(input: $input) {
                        id
                        nombre
                    }
                }
            """
            variables = {
                "input": {
                    "nombre": nombre_cat,
                    "descripcion": f"Productos de {nombre_cat.lower()}"
                }
            }
            
            result = ejecutar_graphql(mutation, variables)
            if result and "createCategoria" in result:
                cat_id = result["createCategoria"]["id"]
                self.categorias_ids[nombre_cat] = cat_id
                self.productos_por_categoria[nombre_cat] = []
                log(f"  ✓ {nombre_cat} (ID: {cat_id})")
                
        log(f"✅ {len(self.categorias_ids)} categorías creadas")
        
    def crear_productos(self):
        """Crear productos realistas con precios y stocks coherentes"""
        log("🛒 Creando productos con datos realistas...")
        
        contador = 0
        for categoria, productos in CATEGORIAS_PRODUCTOS.items():
            cat_id = self.categorias_ids.get(categoria)
            if not cat_id:
                continue
                
            for prod_data in productos:
                # Variación aleatoria en stock (80%-120% del promedio)
                stock_base = prod_data["stock_promedio"]
                stock_actual = int(stock_base * random.uniform(0.8, 1.2))
                
                mutation = """
                    mutation($input: ProductoInput!) {
                        createProducto(input: $input) {
                            id
                            nombre
                            precio
                            stock
                        }
                    }
                """
                variables = {
                    "input": {
                        "nombre": prod_data["nombre"],
                        "descripcion": f"Producto de alta calidad - {categoria}",
                        "precio": prod_data["precio"],
                        "stock": stock_actual,
                        "imagenUrl": f"https://via.placeholder.com/150?text={prod_data['nombre'].replace(' ', '+')}",
                        "categoriaId": cat_id
                    }
                }
                
                result = ejecutar_graphql(mutation, variables)
                if result and "createProducto" in result:
                    prod = result["createProducto"]
                    prod_id = prod["id"]
                    self.productos_ids[prod_data["nombre"]] = {
                        "id": prod_id,
                        "precio": prod["precio"],
                        "stock": prod["stock"],
                        "categoria": categoria
                    }
                    self.productos_por_categoria[categoria].append(prod_id)
                    contador += 1
                    
        log(f"✅ {contador} productos creados con precios y stocks realistas")
        
    def crear_usuarios(self):
        """Crear usuarios del sistema"""
        log("👤 Creando usuarios del sistema...")
        
        usuarios = [
            {"nombre": "Admin Principal", "correo": "admin@supermercado.com", "contrasena": "admin123"},
            {"nombre": "Cajero 1", "correo": "cajero1@supermercado.com", "contrasena": "cajero123"},
            {"nombre": "Gerente", "correo": "gerente@supermercado.com", "contrasena": "gerente123"},
        ]
        
        for usuario in usuarios:
            mutation = """
                mutation($input: UsuarioInput!) {
                    createUsuario(input: $input) {
                        id
                        nombre
                    }
                }
            """
            variables = {"input": usuario}
            
            result = ejecutar_graphql(mutation, variables)
            if result and "createUsuario" in result:
                user_id = result["createUsuario"]["id"]
                self.usuarios_ids[usuario["correo"]] = user_id
                
        log(f"✅ {len(usuarios)} usuarios creados")
        
    def crear_clientes(self):
        """Crear clientes con perfiles realistas"""
        log("👥 Creando clientes con perfiles de comportamiento...")
        
        for perfil in PERFILES_CLIENTES:
            mutation = """
                mutation($input: ClienteInput!) {
                    createCliente(input: $input) {
                        id
                        nombre
                    }
                }
            """
            variables = {
                "input": {
                    "nombre": perfil["nombre"],
                    "correo": perfil["correo"],
                    "telefono": perfil["telefono"]
                }
            }
            
            result = ejecutar_graphql(mutation, variables)
            if result and "createCliente" in result:
                cliente_id = result["createCliente"]["id"]
                self.clientes_ids[perfil["nombre"]] = {
                    "id": cliente_id,
                    "perfil": perfil
                }
                
        log(f"✅ {len(PERFILES_CLIENTES)} clientes creados (3 VIP, 12 Regulares, 10 Ocasionales)")
        
    def crear_ventas_realistas(self):
        """Crear ventas siguiendo patrones realistas de cada cliente"""
        log("🛍️  Generando ventas realistas (últimos 3 meses)...")
        
        fecha_inicio = datetime.now() - timedelta(days=90)
        
        for nombre_cliente, datos in self.clientes_ids.items():
            cliente_id = datos["id"]
            perfil = datos["perfil"]
            
            # Número de compras según frecuencia del perfil
            min_compras, max_compras = perfil["frecuencia_compras"]
            num_compras = random.randint(min_compras * 3, max_compras * 3)  # 3 meses
            
            for _ in range(num_compras):
                # Fecha aleatoria en los últimos 90 días
                dias_atras = random.randint(0, 90)
                fecha_venta = fecha_inicio + timedelta(days=dias_atras)
                
                # Seleccionar productos de categorías favoritas
                productos_venta = []
                categorias_favoritas = perfil["productos_favoritos"]
                
                # Número de productos en la venta (1-5 items)
                num_items = random.randint(1, 5)
                
                for _ in range(num_items):
                    categoria = random.choice(categorias_favoritas)
                    productos_categoria = self.productos_por_categoria.get(categoria, [])
                    
                    if productos_categoria:
                        prod_id = random.choice(productos_categoria)
                        # Buscar info del producto
                        prod_info = next(
                            (p for p in self.productos_ids.values() if p["id"] == prod_id),
                            None
                        )
                        
                        if prod_info:
                            cantidad = random.randint(1, 3)
                            productos_venta.append({
                                "productoId": prod_id,
                                "cantidad": cantidad,
                                "precioUnitario": prod_info["precio"]
                            })
                
                if productos_venta:
                    # Calcular total
                    total = sum(p["cantidad"] * p["precioUnitario"] for p in productos_venta)
                    
                    # Verificar que esté en rango esperado del perfil
                    min_ticket, max_ticket = perfil["ticket_promedio"]
                    
                    # Ajustar si es necesario (agregar más productos o reducir)
                    if total < min_ticket * 0.8:
                        # Agregar más cantidad a productos existentes
                        for p in productos_venta:
                            p["cantidad"] += 1
                        total = sum(p["cantidad"] * p["precioUnitario"] for p in productos_venta)
                    
                    mutation = """
                        mutation($input: VentaInput!) {
                            createVenta(input: $input) {
                                id
                                total
                                fecha
                            }
                        }
                    """
                    variables = {
                        "input": {
                            "clienteId": cliente_id,
                            "fecha": fecha_venta.strftime("%Y-%m-%d"),
                            "detalles": productos_venta
                        }
                    }
                    
                    result = ejecutar_graphql(mutation, variables)
                    if result and "createVenta" in result:
                        self.ventas_generadas += 1
                        
                        if self.ventas_generadas % 20 == 0:
                            log(f"  → {self.ventas_generadas} ventas generadas...")
        
        log(f"✅ {self.ventas_generadas} ventas generadas con patrones realistas")
        
    def mostrar_resumen(self):
        """Mostrar resumen estadístico de datos generados"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS GENERADOS")
        print("="*60)
        print(f"Categorías:      {len(self.categorias_ids)}")
        print(f"Productos:       {len(self.productos_ids)}")
        print(f"Clientes:        {len(self.clientes_ids)}")
        print(f"  - VIP:         {sum(1 for d in self.clientes_ids.values() if d['perfil']['tipo'] == 'VIP')}")
        print(f"  - Regulares:   {sum(1 for d in self.clientes_ids.values() if d['perfil']['tipo'] == 'REGULAR')}")
        print(f"  - Ocasionales: {sum(1 for d in self.clientes_ids.values() if d['perfil']['tipo'] == 'OCASIONAL')}")
        print(f"Usuarios:        {len(self.usuarios_ids)}")
        print(f"Ventas:          {self.ventas_generadas}")
        print(f"Detalles Venta:  ~{self.ventas_generadas * 2.5:.0f} (estimado)")
        print("="*60)
        print("\n✅ DATOS LISTOS PARA:")
        print("  🤖 Machine Learning:")
        print("     - Supervisado: Predicción de precios (Regresión)")
        print("     - No Supervisado: Segmentación de clientes (K-Means)")
        print("     - Semi-supervisado: Detección de anomalías en ventas")
        print("\n  🧠 Deep Learning:")
        print("     - Clasificación de productos por categoría (Transfer Learning)")
        print("     - Usar MobileNetV2 o ResNet50 pre-entrenados")
        print("\n  📈 Reportes y Gráficas:")
        print("     - Ventas por categoría")
        print("     - Top productos más vendidos")
        print("     - Clientes VIP vs Regulares")
        print("     - Tendencias temporales (últimos 3 meses)")
        print("     - Stock vs ventas")
        print("="*60)

# =======================================
# EJECUCIÓN
# =======================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  GENERADOR DE DATOS REALISTAS PARA ML/DL + REPORTES         ║
║  Sistema de Gestión de Supermercado                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  REQUISITOS:")
    print("   1. Backend corriendo en http://localhost:8080")
    print("   2. Base de datos limpia (o datos serán agregados)")
    print("   3. Tiempo estimado: 2-3 minutos")
    print()
    
    respuesta = input("¿Continuar con la generación? (s/n): ").lower()
    
    if respuesta == 's':
        generador = GeneradorDatos()
        generador.generar_todo()
        
        print("\n🎉 ¡DATOS GENERADOS EXITOSAMENTE!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Verificar datos en GraphiQL: http://localhost:8080/graphiql")
        print("   2. Ejecutar notebooks de ML/DL (se crearán a continuación)")
        print("   3. Generar reportes desde el frontend")
        print()
    else:
        print("❌ Generación cancelada")
