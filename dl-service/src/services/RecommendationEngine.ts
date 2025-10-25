/**
 * MOTOR DE RECOMENDACIONES CON DEEP LEARNING
 * 
 * Técnica: Product Embeddings + Collaborative Filtering
 * - Convierte productos a vectores de 32 dimensiones
 * - Aprende relaciones implícitas entre productos
 * - Usa cosine similarity para encontrar productos similares
 * 
 * Basado en patrones de compra conjunta (co-purchase)
 */

import * as tf from '@tensorflow/tfjs-node';
import axios from 'axios';

// Leer desde variable de entorno, con fallback a localhost para desarrollo local
const CORE_SERVICE_URL = process.env.CORE_SERVICE_URL || 'http://localhost:8080/graphql';
const EMBEDDING_DIM = 32; // Dimensión del espacio de embeddings
const EPOCHS = 30; // Épocas de entrenamiento

interface ProductoRelacionado {
  id: number;
  nombre: string;
  categoria: string;
  score_relacion: number;
  razon: string;
}

interface Venta {
  id: number;
  detalles: Array<{
    producto: {
      id: number | string;
    };
  }>;
}

class RecommendationEngine {
  private embeddings: Map<number, number[]> = new Map();
  private productosInfo: Map<number, { nombre: string; categoria: string }> = new Map();
  private modeloEntrenado: boolean = false;
  private ultimoEntrenamiento: number = 0;
  private readonly CACHE_DURATION = 3600000; // 1 hora

  /**
   * Obtener datos de co-compra desde Core Service
   */
  private async obtenerDatosCoCompra(): Promise<Map<number, Set<number>>> {
    try {
      console.log('🔍 Obteniendo datos de co-compra desde Core Service...');

      const query = `
        query {
          ventas {
            id
            detalles {
              producto {
                id
              }
            }
          }
          productos {
            id
            nombre
            categoria {
              nombre
            }
          }
        }
      `;

      const response = await axios.post(
        CORE_SERVICE_URL,
        { query },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 5000
        }
      );

      if (response.data.errors) {
        console.warn('⚠️ Error en GraphQL:', response.data.errors);
        return this.generarDatosSimulados();
      }

      const ventas: Venta[] = response.data.data?.ventas || [];
      const productos = response.data.data?.productos || [];

      // Guardar info de productos
      productos.forEach((p: any) => {
        const productoId = typeof p.id === 'string' ? parseInt(p.id, 10) : p.id;
        this.productosInfo.set(productoId, {
          nombre: p.nombre,
          categoria: p.categoria?.nombre || 'Sin categoría'
        });
      });

      // Construir matriz de co-compra
      const coCompra = new Map<number, Set<number>>();

      ventas.forEach(venta => {
        const productosEnVenta = venta.detalles.map(d => {
          const id = d.producto.id;
          return typeof id === 'string' ? parseInt(id, 10) : id;
        });
        
        // Cada producto en la venta está relacionado con los demás
        productosEnVenta.forEach(p1 => {
          if (!coCompra.has(p1)) {
            coCompra.set(p1, new Set());
          }
          
          productosEnVenta.forEach(p2 => {
            if (p1 !== p2) {
              coCompra.get(p1)!.add(p2);
            }
          });
        });
      });

      console.log(`✅ Obtenidos ${ventas.length} ventas con ${coCompra.size} productos únicos`);
      return coCompra;

    } catch (error) {
      console.warn('⚠️ Error conectando con Core Service, usando datos simulados');
      return this.generarDatosSimulados();
    }
  }

  /**
   * Generar datos simulados si no hay conexión
   */
  private generarDatosSimulados(): Map<number, Set<number>> {
    const coCompra = new Map<number, Set<number>>();
    
    // Simular relaciones lógicas (productos que se compran juntos)
    const relaciones = [
      [1, 2, 3], // Bebidas juntas
      [8, 9, 10], // Lácteos juntos
      [13, 14, 15], // Panadería junta
      [24, 25, 26], // Frutas juntas
      [30, 31, 32], // Verduras juntas
      [1, 41], // Bebida + Snack
      [8, 13], // Leche + Pan
      [19, 30], // Carne + Verduras
    ];

    relaciones.forEach(grupo => {
      grupo.forEach(p1 => {
        if (!coCompra.has(p1)) {
          coCompra.set(p1, new Set());
        }
        grupo.forEach(p2 => {
          if (p1 !== p2) {
            coCompra.get(p1)!.add(p2);
          }
        });
      });
    });

    return coCompra;
  }

  /**
   * Crear embeddings usando matriz de co-compra
   * Técnica simplificada de Word2Vec adaptada a productos
   */
  private async crearEmbeddings(coCompra: Map<number, Set<number>>): Promise<void> {
    console.log('🧠 Creando embeddings de productos con DL...');

    const productosIds = Array.from(coCompra.keys());
    const numProductos = productosIds.length;

    if (numProductos < 2) {
      console.warn('⚠️ Datos insuficientes para crear embeddings');
      return;
    }

    // Crear matriz de co-ocurrencia normalizada
    const matrizCoOcurrencia: number[][] = [];
    
    productosIds.forEach(p1 => {
      const fila: number[] = [];
      const relacionados = coCompra.get(p1) || new Set();
      
      productosIds.forEach(p2 => {
        fila.push(relacionados.has(p2) ? 1 : 0);
      });
      
      matrizCoOcurrencia.push(fila);
    });

    // Crear modelo simple de embedding (Autoencoder)
    const modelo = tf.sequential({
      layers: [
        // Capa de encoding (comprime a embedding_dim)
        tf.layers.dense({
          units: EMBEDDING_DIM,
          activation: 'relu',
          inputShape: [numProductos]
        }),
        
        // Capa de decoding (reconstruye)
        tf.layers.dense({
          units: numProductos,
          activation: 'sigmoid'
        })
      ]
    });

    modelo.compile({
      optimizer: tf.train.adam(0.01),
      loss: 'binaryCrossentropy'
    });

    // Entrenar autoencoder
    const xTensor = tf.tensor2d(matrizCoOcurrencia);
    
    await modelo.fit(xTensor, xTensor, {
      epochs: EPOCHS,
      batchSize: 8,
      verbose: 0,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          if (epoch % 10 === 0) {
            console.log(`  Época ${epoch}/${EPOCHS} - Loss: ${logs?.loss.toFixed(4)}`);
          }
        }
      }
    });

    // Extraer embeddings (activaciones de la capa oculta)
    const encoderModel = tf.sequential({
      layers: modelo.layers.slice(0, 1) // Solo la primera capa (encoder)
    });

    const embeddingsTensor = encoderModel.predict(xTensor) as tf.Tensor;
    const embeddingsArray = await embeddingsTensor.array() as number[][];

    // Guardar embeddings
    productosIds.forEach((productoId, index) => {
      this.embeddings.set(productoId, embeddingsArray[index]);
    });

    // Limpiar memoria de tensores
    xTensor.dispose();
    embeddingsTensor.dispose();
    
    // Limpiar modelos (evitar doble dispose)
    try {
      encoderModel.dispose();
      modelo.dispose();
    } catch (error) {
      // Ignorar errores de dispose si ya están liberados
      console.log('⚠️ Modelos ya liberados de memoria');
    }

    console.log(`✅ Embeddings creados para ${productosIds.length} productos`);
  }

  /**
   * Calcular similitud coseno entre dos vectores
   */
  private cosineSimilarity(vec1: number[], vec2: number[]): number {
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      norm1 += vec1[i] * vec1[i];
      norm2 += vec2[i] * vec2[i];
    }

    const magnitude = Math.sqrt(norm1) * Math.sqrt(norm2);
    return magnitude === 0 ? 0 : dotProduct / magnitude;
  }

  /**
   * Entrenar modelo de recomendaciones
   */
  async entrenar(): Promise<void> {
    const ahora = Date.now();
    
    // Verificar cache
    if (this.modeloEntrenado && (ahora - this.ultimoEntrenamiento < this.CACHE_DURATION)) {
      console.log('📦 Modelo ya entrenado y en cache');
      return;
    }

    console.log('🚀 Entrenando sistema de recomendaciones con DL...');

    const coCompra = await this.obtenerDatosCoCompra();
    await this.crearEmbeddings(coCompra);

    this.modeloEntrenado = true;
    this.ultimoEntrenamiento = ahora;

    console.log('✅ Sistema de recomendaciones entrenado');
  }

  /**
   * Obtener productos recomendados para un producto dado
   */
  async obtenerRecomendaciones(
    productoId: number,
    topN: number = 4
  ): Promise<ProductoRelacionado[]> {
    // Entrenar si no está entrenado
    if (!this.modeloEntrenado) {
      await this.entrenar();
    }

    const embeddingProducto = this.embeddings.get(productoId);
    
    if (!embeddingProducto) {
      console.warn(`⚠️ No hay embedding para producto ${productoId}, usando fallback`);
      return this.recomendacionesFallback(productoId, topN);
    }

    // Calcular similitud con todos los demás productos
    const similitudes: Array<{ id: number; score: number }> = [];

    this.embeddings.forEach((embedding, id) => {
      if (id !== productoId) {
        const similitud = this.cosineSimilarity(embeddingProducto, embedding);
        similitudes.push({ id, score: similitud });
      }
    });

    // Ordenar por similitud (mayor a menor)
    similitudes.sort((a, b) => b.score - a.score);

    // Tomar top N
    const recomendaciones: ProductoRelacionado[] = similitudes
      .slice(0, topN)
      .map(({ id, score }) => {
        const info = this.productosInfo.get(id);
        return {
          id,
          nombre: info?.nombre || `Producto ${id}`,
          categoria: info?.categoria || 'Desconocida',
          score_relacion: score,
          razon: 'Recomendado por Deep Learning (embeddings)'
        };
      });

    console.log(`✅ Generadas ${recomendaciones.length} recomendaciones DL para producto ${productoId}`);
    return recomendaciones;
  }

  /**
   * Fallback: recomendaciones simples si no hay embeddings
   */
  private recomendacionesFallback(productoId: number, topN: number): ProductoRelacionado[] {
    const productoInfo = this.productosInfo.get(productoId);
    if (!productoInfo) return [];

    // Buscar productos de la misma categoría
    const relacionados: ProductoRelacionado[] = [];
    
    this.productosInfo.forEach((info, id) => {
      if (id !== productoId && info.categoria === productoInfo.categoria && relacionados.length < topN) {
        relacionados.push({
          id,
          nombre: info.nombre,
          categoria: info.categoria,
          score_relacion: 0.75,
          razon: 'Misma categoría (fallback)'
        });
      }
    });

    return relacionados;
  }

  /**
   * Limpiar cache
   */
  limpiarCache(): void {
    this.embeddings.clear();
    this.productosInfo.clear();
    this.modeloEntrenado = false;
    console.log('🧹 Cache de recomendaciones limpiado');
  }
}

// Export singleton
export const recommendationEngine = new RecommendationEngine();
export default RecommendationEngine;
