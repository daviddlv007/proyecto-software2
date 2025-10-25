/**
 * SERVICIO UNIFICADO DE IDENTIFICACIÓN DE PRODUCTOS
 * 
 * Flujo completo:
 * 1. Identificar producto desde imagen (MobileNet)
 * 2. Mapear a productos del inventario en español
 * 3. Predecir ventas futuras del producto
 * 4. Obtener productos relacionados
 * 
 * Base de datos: Productos del script generar_datos_ml_realistas.py
 */

import * as tf from '@tensorflow/tfjs-node';
import * as mobilenet from '@tensorflow-models/mobilenet';
import sharp from 'sharp';
import { salesPredictorReal } from './SalesPredictorReal';
import { recommendationEngine } from './RecommendationEngine';

// ============================================
// TIPOS
// ============================================

interface ProductoInventario {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  stock: number;
  keywords_mobilenet: string[];  // Keywords de MobileNet que mapean a este producto
}

interface ResultadoIdentificacion {
  success: boolean;
  producto: {
    id: number;
    nombre: string;
    categoria: string;
    precio: number;
    stock: number;
    confianza: number;
  } | null;
  prediccion_ventas: {
    proximos_7_dias: number[];
    tendencia: string;
    promedio_diario: number;
    confianza?: number;
    metodo?: 'LSTM' | 'Simulado';
  } | null;
  productos_relacionados: Array<{
    id: number;
    nombre: string;
    categoria: string;
    score_relacion: number;
    razon: string;
  }>;
  predicciones_raw: Array<{
    clase_mobilenet: string;
    probabilidad: number;
  }>;
  mensaje: string;
}

// ============================================
// BASE DE DATOS EN MEMORIA (Productos Reales)
// ============================================

const PRODUCTOS_INVENTARIO: ProductoInventario[] = [
  // BEBIDAS
  {
    id: 1,
    nombre: "Coca-Cola 2L",
    categoria: "Bebidas",
    precio: 2.50,
    stock: 80,
    keywords_mobilenet: ['pop bottle', 'soda bottle', 'water bottle', 'bottle']
  },
  {
    id: 2,
    nombre: "Sprite 2L",
    categoria: "Bebidas",
    precio: 2.50,
    stock: 70,
    keywords_mobilenet: ['pop bottle', 'soda bottle', 'water bottle', 'bottle']
  },
  {
    id: 3,
    nombre: "Fanta 2L",
    categoria: "Bebidas",
    precio: 2.50,
    stock: 60,
    keywords_mobilenet: ['pop bottle', 'soda bottle', 'bottle']
  },
  {
    id: 4,
    nombre: "Agua Mineral 1L",
    categoria: "Bebidas",
    precio: 0.80,
    stock: 150,
    keywords_mobilenet: ['water bottle', 'plastic bottle', 'bottle']
  },
  {
    id: 5,
    nombre: "Jugo de Naranja 1L",
    categoria: "Bebidas",
    precio: 3.20,
    stock: 50,
    keywords_mobilenet: ['water bottle', 'bottle', 'pitcher']
  },
  {
    id: 6,
    nombre: "Cerveza Pilsener 355ml",
    categoria: "Bebidas",
    precio: 1.00,
    stock: 120,
    keywords_mobilenet: ['beer bottle', 'beer glass', 'bottle']
  },
  {
    id: 7,
    nombre: "Energizante Red Bull",
    categoria: "Bebidas",
    precio: 1.80,
    stock: 40,
    keywords_mobilenet: ['pop bottle', 'can', 'bottle']
  },
  
  // LÁCTEOS
  {
    id: 8,
    nombre: "Leche Entera 1L",
    categoria: "Lácteos",
    precio: 1.20,
    stock: 100,
    keywords_mobilenet: ['milk can', 'carton', 'jug']
  },
  {
    id: 9,
    nombre: "Yogurt Natural 1L",
    categoria: "Lácteos",
    precio: 2.80,
    stock: 60,
    keywords_mobilenet: ['milk can', 'pitcher', 'bottle']
  },
  {
    id: 10,
    nombre: "Queso Fresco 500g",
    categoria: "Lácteos",
    precio: 4.50,
    stock: 40,
    keywords_mobilenet: ['cheese']
  },
  {
    id: 11,
    nombre: "Mantequilla 250g",
    categoria: "Lácteos",
    precio: 2.30,
    stock: 50,
    keywords_mobilenet: ['butter', 'cheese']
  },
  {
    id: 12,
    nombre: "Yogurt Griego",
    categoria: "Lácteos",
    precio: 3.50,
    stock: 35,
    keywords_mobilenet: ['milk can', 'cup']
  },
  
  // PANADERÍA
  {
    id: 13,
    nombre: "Pan Blanco",
    categoria: "Panadería",
    precio: 0.25,
    stock: 200,
    keywords_mobilenet: ['bagel', 'bread', 'french loaf', 'baguette', 'pretzel']
  },
  {
    id: 14,
    nombre: "Pan Integral",
    categoria: "Panadería",
    precio: 0.35,
    stock: 150,
    keywords_mobilenet: ['bread', 'french loaf', 'bagel']
  },
  {
    id: 15,
    nombre: "Galletas Saladas",
    categoria: "Panadería",
    precio: 1.50,
    stock: 80,
    keywords_mobilenet: ['pretzel', 'cracker']
  },
  {
    id: 16,
    nombre: "Galletas Dulces",
    categoria: "Panadería",
    precio: 1.80,
    stock: 75,
    keywords_mobilenet: ['cookie', 'pretzel']
  },
  {
    id: 17,
    nombre: "Pastel Chocolate",
    categoria: "Panadería",
    precio: 8.50,
    stock: 15,
    keywords_mobilenet: ['chocolate', 'cake', 'dessert']
  },
  {
    id: 18,
    nombre: "Croissant",
    categoria: "Panadería",
    precio: 1.20,
    stock: 40,
    keywords_mobilenet: ['croissant', 'crescent roll', 'bread']
  },
  
  // CARNES
  {
    id: 19,
    nombre: "Pollo Entero kg",
    categoria: "Carnes",
    precio: 3.50,
    stock: 60,
    keywords_mobilenet: ['drumstick', 'chicken', 'roast']
  },
  {
    id: 20,
    nombre: "Carne de Res kg",
    categoria: "Carnes",
    precio: 8.50,
    stock: 40,
    keywords_mobilenet: ['meat loaf', 'beef', 'steak']
  },
  {
    id: 21,
    nombre: "Cerdo Chuleta kg",
    categoria: "Carnes",
    precio: 6.20,
    stock: 35,
    keywords_mobilenet: ['meat loaf', 'pork', 'chop']
  },
  {
    id: 22,
    nombre: "Pescado Tilapia kg",
    categoria: "Carnes",
    precio: 5.80,
    stock: 30,
    keywords_mobilenet: ['fish', 'salmon']
  },
  {
    id: 23,
    nombre: "Salchicha Pack 500g",
    categoria: "Carnes",
    precio: 3.20,
    stock: 70,
    keywords_mobilenet: ['hot dog', 'sausage', 'frankfurter']
  },
  
  // FRUTAS (ALTA PRIORIDAD - Bien reconocidas por MobileNet)
  {
    id: 24,
    nombre: "Manzana kg",
    categoria: "Frutas",
    precio: 1.50,
    stock: 100,
    keywords_mobilenet: ['granny smith', 'apple', 'red delicious', 'golden delicious']
  },
  {
    id: 25,
    nombre: "Plátano kg",
    categoria: "Frutas",
    precio: 0.80,
    stock: 120,
    keywords_mobilenet: ['banana']
  },
  {
    id: 26,
    nombre: "Naranja kg",
    categoria: "Frutas",
    precio: 1.20,
    stock: 90,
    keywords_mobilenet: ['orange', 'citrus']
  },
  {
    id: 27,
    nombre: "Uva kg",
    categoria: "Frutas",
    precio: 3.50,
    stock: 50,
    keywords_mobilenet: ['grape']
  },
  {
    id: 28,
    nombre: "Sandía Unidad",
    categoria: "Frutas",
    precio: 4.00,
    stock: 25,
    keywords_mobilenet: ['watermelon']
  },
  {
    id: 29,
    nombre: "Piña Unidad",
    categoria: "Frutas",
    precio: 2.50,
    stock: 40,
    keywords_mobilenet: ['pineapple', 'ananas']
  },
  
  // VERDURAS
  {
    id: 30,
    nombre: "Tomate kg",
    categoria: "Verduras",
    precio: 1.20,
    stock: 80,
    keywords_mobilenet: ['tomato']
  },
  {
    id: 31,
    nombre: "Cebolla kg",
    categoria: "Verduras",
    precio: 0.90,
    stock: 100,
    keywords_mobilenet: ['onion']
  },
  {
    id: 32,
    nombre: "Zanahoria kg",
    categoria: "Verduras",
    precio: 0.70,
    stock: 90,
    keywords_mobilenet: ['carrot']
  },
  {
    id: 33,
    nombre: "Lechuga Unidad",
    categoria: "Verduras",
    precio: 0.60,
    stock: 70,
    keywords_mobilenet: ['lettuce', 'cabbage']
  },
  {
    id: 34,
    nombre: "Brócoli kg",
    categoria: "Verduras",
    precio: 1.80,
    stock: 50,
    keywords_mobilenet: ['broccoli', 'cauliflower']
  },
  {
    id: 35,
    nombre: "Papa kg",
    categoria: "Verduras",
    precio: 0.50,
    stock: 150,
    keywords_mobilenet: ['potato', 'baked potato']
  },
  
  // LIMPIEZA
  {
    id: 36,
    nombre: "Detergente 1kg",
    categoria: "Limpieza",
    precio: 3.50,
    stock: 60,
    keywords_mobilenet: ['soap dispenser', 'bottle']
  },
  {
    id: 37,
    nombre: "Jabón Líquido 500ml",
    categoria: "Limpieza",
    precio: 2.80,
    stock: 70,
    keywords_mobilenet: ['soap dispenser', 'bottle', 'lotion']
  },
  {
    id: 38,
    nombre: "Papel Higiénico 4u",
    categoria: "Limpieza",
    precio: 2.20,
    stock: 100,
    keywords_mobilenet: ['toilet tissue', 'paper towel']
  },
  {
    id: 39,
    nombre: "Cloro 1L",
    categoria: "Limpieza",
    precio: 1.50,
    stock: 80,
    keywords_mobilenet: ['bottle', 'jug']
  },
  {
    id: 40,
    nombre: "Esponja Pack 3u",
    categoria: "Limpieza",
    precio: 1.20,
    stock: 90,
    keywords_mobilenet: ['sponge', 'dishrag']
  },
  
  // SNACKS
  {
    id: 41,
    nombre: "Papas Fritas 150g",
    categoria: "Snacks",
    precio: 1.50,
    stock: 100,
    keywords_mobilenet: ['french fries', 'chip', 'potato']
  },
  {
    id: 42,
    nombre: "Doritos 200g",
    categoria: "Snacks",
    precio: 2.20,
    stock: 85,
    keywords_mobilenet: ['chip', 'corn']
  },
  {
    id: 43,
    nombre: "Chocolate Snickers",
    categoria: "Snacks",
    precio: 0.80,
    stock: 120,
    keywords_mobilenet: ['chocolate', 'candy bar']
  },
  {
    id: 44,
    nombre: "Caramelos Bolsa",
    categoria: "Snacks",
    precio: 0.50,
    stock: 150,
    keywords_mobilenet: ['candy', 'lollipop']
  },
  {
    id: 45,
    nombre: "Maní Salado 100g",
    categoria: "Snacks",
    precio: 1.20,
    stock: 70,
    keywords_mobilenet: ['peanut', 'nut']
  },
  {
    id: 46,
    nombre: "Chicles Pack",
    categoria: "Snacks",
    precio: 0.30,
    stock: 180,
    keywords_mobilenet: ['gum', 'candy']
  }
];

// ============================================
// SERVICIO PRINCIPAL
// ============================================

class ServicioIdentificacionUnificado {
  private modelo: mobilenet.MobileNet | null = null;
  private cargando = false;

  /**
   * Cargar MobileNet (solo una vez)
   */
  async cargarModelo(): Promise<void> {
    if (this.modelo) return;
    
    if (this.cargando) {
      while (this.cargando) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      return;
    }

    try {
      this.cargando = true;
      console.log('📥 Cargando MobileNet v2...');
      this.modelo = await mobilenet.load({ version: 2, alpha: 1.0 });
      console.log('✅ MobileNet cargado y listo');
    } catch (error) {
      console.error('❌ Error cargando MobileNet:', error);
      throw error;
    } finally {
      this.cargando = false;
    }
  }

  /**
   * ENDPOINT PRINCIPAL: Identificar producto + predicciones + relacionados
   */
  async identificarProductoCompleto(imagePath: string): Promise<ResultadoIdentificacion> {
    try {
      await this.cargarModelo();
      if (!this.modelo) throw new Error('Modelo no disponible');

      console.log(`🔍 Identificando producto desde: ${imagePath}`);

      // 1. Procesar imagen con Sharp + TensorFlow
      const imageBuffer = await sharp(imagePath)
        .resize(224, 224)
        .jpeg()
        .toBuffer();

      const imageTensor = tf.node.decodeImage(imageBuffer, 3) as tf.Tensor3D;
      const batched = imageTensor.expandDims(0);

      // 2. Clasificar con MobileNet
      const predicciones = await this.modelo.classify(batched as any, 10);

      // Limpiar memoria
      imageTensor.dispose();
      batched.dispose();

      console.log('🎯 Top 5 predicciones MobileNet:', 
        predicciones.slice(0, 5).map(p => `${p.className}: ${(p.probability * 100).toFixed(2)}%`)
      );

      // 3. Mapear a producto del inventario
      const productoIdentificado = this.mapearAProducto(predicciones);

      if (!productoIdentificado) {
        return {
          success: false,
          producto: null,
          prediccion_ventas: null,
          productos_relacionados: [],
          predicciones_raw: predicciones.slice(0, 5).map(p => ({
            clase_mobilenet: p.className,
            probabilidad: p.probability
          })),
          mensaje: 'No se pudo identificar el producto. No coincide con ningún producto del inventario.'
        };
      }

      // 4. Predecir ventas futuras con LSTM (Deep Learning REAL)
      console.log('📈 Prediciendo ventas con LSTM...');
      const prediccionVentas = await salesPredictorReal.predecirVentas(productoIdentificado.id);

      // 5. Obtener productos relacionados con DL (Embeddings + Collaborative Filtering)
      console.log('🔗 Obteniendo recomendaciones con Deep Learning...');
      const productosRelacionados = await recommendationEngine.obtenerRecomendaciones(productoIdentificado.id, 4);

      return {
        success: true,
        producto: productoIdentificado,
        prediccion_ventas: prediccionVentas,
        productos_relacionados: productosRelacionados,
        predicciones_raw: predicciones.slice(0, 5).map(p => ({
          clase_mobilenet: p.className,
          probabilidad: p.probability
        })),
        mensaje: `✅ Producto identificado: ${productoIdentificado.nombre} (${(productoIdentificado.confianza * 100).toFixed(1)}% confianza)`
      };

    } catch (error) {
      console.error('❌ Error en identificación:', error);
      throw error;
    }
  }

  /**
   * Mapear predicciones de MobileNet a productos del inventario en español
   */
  private mapearAProducto(predicciones: any[]): typeof PRODUCTOS_INVENTARIO[0] & { confianza: number } | null {
    for (const pred of predicciones) {
      const classNameLower = pred.className.toLowerCase();
      
      // Buscar producto que tenga keyword que coincida
      for (const producto of PRODUCTOS_INVENTARIO) {
        for (const keyword of producto.keywords_mobilenet) {
          if (classNameLower.includes(keyword.toLowerCase())) {
            console.log(`✅ Match encontrado: "${pred.className}" → ${producto.nombre} (${producto.categoria})`);
            return {
              ...producto,
              confianza: pred.probability
            };
          }
        }
      }
    }
    
    return null;
  }

  /**
  }

  /**
   * Obtener todos los productos disponibles
   */
  public obtenerTodosLosProductos() {
    return PRODUCTOS_INVENTARIO.map(p => ({
      id: p.id,
      nombre: p.nombre,
      categoria: p.categoria,
      precio: p.precio,
      stock: p.stock
    }));
  }
}

export default new ServicioIdentificacionUnificado();
