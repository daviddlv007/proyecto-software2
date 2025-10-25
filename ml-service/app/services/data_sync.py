"""
Servicio de sincronización con core-service (GraphQL)
Consulta datos transaccionales y los almacena en caché local
"""
import httpx
import os
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import ProductoCache, VentaCache, ClienteMetrics
import logging

logger = logging.getLogger(__name__)

# Leer desde variable de entorno, con fallback a localhost para desarrollo local
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://localhost:8080/graphql")


async def fetch_productos():
    """Consultar productos desde core-service"""
    query = """
        query {
            productos {
                id
                nombre
                precio
                stock
                categoria { nombre }
            }
        }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CORE_SERVICE_URL,
            json={"query": query},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("productos", [])
        else:
            logger.error(f"Error fetching productos: {response.status_code}")
            return []


async def fetch_ventas():
    """Consultar ventas desde core-service"""
    query = """
        query {
            ventas {
                id
                cliente { id }
                fecha
                total
                detalles { id }
            }
        }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CORE_SERVICE_URL,
            json={"query": query},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("ventas", [])
        else:
            logger.error(f"Error fetching ventas: {response.status_code}")
            return []


async def fetch_clientes():
    """Consultar clientes desde core-service"""
    query = """
        query {
            clientes {
                id
                nombre
                correo
            }
        }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CORE_SERVICE_URL,
            json={"query": query},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("clientes", [])
        else:
            logger.error(f"Error fetching clientes: {response.status_code}")
            return []


async def sync_data(db: Session):
    """
    Sincroniza todos los datos del core-service
    Limpia caché anterior y reconstruye
    """
    logger.info("🔄 Iniciando sincronización con core-service...")
    
    # Limpiar caché
    db.query(ProductoCache).delete()
    db.query(VentaCache).delete()
    db.query(ClienteMetrics).delete()
    
    # Sincronizar productos
    productos = await fetch_productos()
    productos_count = 0
    for p in productos:
        producto_cache = ProductoCache(
            id=int(p["id"]),
            nombre=p["nombre"],
            categoria=p.get("categoria", {}).get("nombre", "Sin categoría") if p.get("categoria") else "Sin categoría",
            precio=float(p["precio"]),
            stock=int(p.get("stock", 0))
        )
        db.add(producto_cache)
        productos_count += 1
    
    # Sincronizar ventas
    ventas = await fetch_ventas()
    ventas_count = 0
    cliente_stats = {}
    
    for v in ventas:
        venta_cache = VentaCache(
            id=int(v["id"]),
            cliente_id=int(v["cliente"]["id"]) if v.get("cliente") else 0,
            fecha=v.get("fecha", ""),
            total=float(v["total"]),
            num_productos=len(v.get("detalles", []))
        )
        db.add(venta_cache)
        ventas_count += 1
        
        # Agregar stats por cliente
        if v.get("cliente"):
            cid = int(v["cliente"]["id"])
            if cid not in cliente_stats:
                cliente_stats[cid] = {
                    "nombre": f"Cliente {cid}",  # Nombre simplificado
                    "total": 0.0,
                    "count": 0
                }
            cliente_stats[cid]["total"] += float(v["total"])
            cliente_stats[cid]["count"] += 1
    
    # Calcular métricas de clientes
    clientes_count = 0
    for cid, stats in cliente_stats.items():
        ticket_prom = stats["total"] / stats["count"] if stats["count"] > 0 else 0
        
        # Segmentación básica por ticket promedio y frecuencia
        if stats["count"] >= 4 and ticket_prom >= 25:
            segmento = "VIP"
        elif stats["count"] >= 2 and ticket_prom >= 12:
            segmento = "Regular"
        else:
            segmento = "Ocasional"
        
        cliente_metric = ClienteMetrics(
            cliente_id=cid,
            nombre=stats["nombre"],
            total_compras=stats["total"],
            frecuencia=stats["count"],
            ticket_promedio=ticket_prom,
            segmento=segmento
        )
        db.add(cliente_metric)
        clientes_count += 1
    
    db.commit()
    
    logger.info(f"✅ Sincronización completada:")
    logger.info(f"   - Productos: {productos_count}")
    logger.info(f"   - Ventas: {ventas_count}")
    logger.info(f"   - Clientes: {clientes_count}")
    
    return {
        "productos_synced": productos_count,
        "ventas_synced": ventas_count,
        "clientes_synced": clientes_count,
        "timestamp": datetime.utcnow()
    }


async def check_core_service_health():
    """Verificar si core-service está disponible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                CORE_SERVICE_URL,
                json={"query": "{ __typename }"},
                timeout=3.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Core service unreachable: {e}")
        return False
