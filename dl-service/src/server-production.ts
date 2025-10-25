/**
 * DL SERVICE - IDENTIFICACIÓN UNIFICADA DE PRODUCTOS
 * 
 * Endpoint único: POST /api/identificar-producto
 * - Identificación por imagen (MobileNet)
 * - Predicción de ventas (LSTM simulado)
 * - Productos relacionados
 * 
 * Productos en español basados en generar_datos_ml_realistas.py
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import UnifiedProductService from './services/UnifiedProductService';

// ===================================
// CONFIGURACIÓN
// ===================================

const PORT = process.env.PORT || 8082;
const UPLOAD_DIR = path.join(__dirname, '../uploads');

const app = express();

app.use(cors({
  origin: [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://localhost:5174'
  ],
  credentials: true
}));
app.use(express.json());

// Crear directorio de uploads
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Servir archivos estáticos (imágenes subidas)
app.use('/uploads', express.static(UPLOAD_DIR));

// Configurar multer para subida de imágenes
const upload = multer({
  storage: multer.diskStorage({
    destination: UPLOAD_DIR,
    filename: (_req, file, cb) => {
      const uniqueName = Date.now() + '-' + Math.random().toString(36).substring(7) + path.extname(file.originalname);
      cb(null, uniqueName);
    }
  }),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB máximo
  fileFilter: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Solo se permiten imágenes (JPG, PNG, GIF, WEBP)'));
    }
  }
});

// ===================================
// ENDPOINT PRINCIPAL
// ===================================

/**
 * POST /api/identificar-producto
 * 
 * Flujo completo de identificación:
 * 1. Usuario sube imagen
 * 2. MobileNet identifica y mapea a producto en español
 * 3. Se predicen ventas futuras
 * 4. Se retornan productos relacionados
 * 
 * @param image - Archivo de imagen (multipart/form-data)
 * @returns Producto identificado + predicciones + relacionados
 */
app.post('/api/identificar-producto', upload.single('image'), async (req: Request, res: Response): Promise<void> => {
  try {
    // Validar que se envió una imagen
    if (!req.file) {
      res.status(400).json({
        success: false,
        error: 'No se proporcionó ninguna imagen',
        mensaje: 'Por favor, sube una imagen del producto'
      });
      return;
    }

    console.log(`\n🔍 Nueva solicitud de identificación`);
    console.log(`   Archivo: ${req.file.filename}`);
    console.log(`   Tamaño: ${(req.file.size / 1024).toFixed(2)} KB`);

    // Procesar identificación completa
    const resultado = await UnifiedProductService.identificarProductoCompleto(req.file.path);

    // Agregar URL de la imagen subida
    const respuesta = {
      ...resultado,
      imagen_url: `/uploads/${req.file.filename}`,
      timestamp: new Date().toISOString()
    };

    // Log del resultado
    if (resultado.success && resultado.producto) {
      console.log(`   ✅ Identificado: ${resultado.producto.nombre}`);
      console.log(`   💰 Precio: $${resultado.producto.precio}`);
      console.log(`   📊 Stock: ${resultado.producto.stock} unidades`);
      console.log(`   🎯 Confianza: ${(resultado.producto.confianza * 100).toFixed(1)}%`);
    } else {
      console.log(`   ❌ No se pudo identificar el producto`);
    }

    res.json(respuesta);

  } catch (error) {
    console.error('❌ Error en identificación:', error);
    res.status(500).json({
      success: false,
      error: 'Error interno del servidor',
      mensaje: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

// ===================================
// ENDPOINTS AUXILIARES
// ===================================

/**
 * GET /health
 * Verificar estado del servicio
 */
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'ok',
    service: 'DL Service - Identificación de Productos',
    timestamp: new Date().toISOString(),
    modelo: 'MobileNet v2',
    endpoints: {
      identificar: 'POST /api/identificar-producto'
    }
  });
});

/**
 * GET /api/productos
 * Listar todos los productos disponibles para identificación
 */
app.get('/api/productos', (_req: Request, res: Response) => {
  const productos = UnifiedProductService.obtenerTodosLosProductos();
  
  res.json({
    success: true,
    total: productos.length,
    productos: productos,
    categorias: ['Bebidas', 'Lácteos', 'Panadería', 'Carnes', 'Frutas', 'Verduras', 'Limpieza', 'Snacks'],
    mensaje: 'Lista de productos disponibles para identificación'
  });
});

/**
 * POST /api/sync
 * Sincronizar datos con Core Service
 * En producción, esto fetcharía productos desde el Core Service GraphQL
 * Por ahora, simula una sincronización exitosa
 */
app.post('/api/sync', async (_req: Request, res: Response) => {
  try {
    console.log('\n🔄 Sincronizando con Core Service...');
    
    // Simulamos una operación asíncrona
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const productos = UnifiedProductService.obtenerTodosLosProductos();
    
    res.json({
      success: true,
      mensaje: 'Sincronización completada exitosamente',
      detalles: {
        productos_sincronizados: productos.length,
        categorias: 8,
        modelo: 'MobileNet v2',
        estado: 'Listo para identificar productos'
      },
      timestamp: new Date().toISOString()
    });
    
    console.log('✅ Sincronización completada');
  } catch (error) {
    console.error('❌ Error en sincronización:', error);
    res.status(500).json({
      success: false,
      error: 'Error al sincronizar con Core Service',
      mensaje: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * POST /api/train
 * Entrenar sistema de recomendaciones con Deep Learning
 * Usa datos de co-compra para crear embeddings de productos
 */
app.post('/api/train', async (_req: Request, res: Response) => {
  try {
    console.log('\n🧠 Entrenando sistema de recomendaciones con DL...');
    
    const { recommendationEngine } = await import('./services/RecommendationEngine');
    await recommendationEngine.entrenar();
    
    res.json({
      success: true,
      mensaje: 'Sistema de recomendaciones entrenado exitosamente',
      detalles: {
        metodo: 'Product Embeddings + Collaborative Filtering',
        dimensiones_embedding: 32,
        epocas: 30,
        tecnica: 'Autoencoder con Deep Learning'
      },
      timestamp: new Date().toISOString()
    });
    
    console.log('✅ Entrenamiento completado');
  } catch (error) {
    console.error('❌ Error en entrenamiento:', error);
    res.status(500).json({
      success: false,
      error: 'Error al entrenar modelo de recomendaciones',
      mensaje: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /api/recomendaciones/:productoId
 * Obtener recomendaciones para un producto específico
 */
app.get('/api/recomendaciones/:productoId', async (req: Request, res: Response) => {
  try {
    const productoId = parseInt(req.params.productoId);
    
    if (isNaN(productoId)) {
      res.status(400).json({
        success: false,
        error: 'ID de producto inválido'
      });
      return;
    }

    console.log(`\n🔗 Obteniendo recomendaciones para producto ${productoId}...`);
    
    const { recommendationEngine } = await import('./services/RecommendationEngine');
    const recomendaciones = await recommendationEngine.obtenerRecomendaciones(productoId, 4);
    
    res.json({
      success: true,
      producto_id: productoId,
      recomendaciones: recomendaciones,
      total: recomendaciones.length
    });
    
    console.log(`✅ Generadas ${recomendaciones.length} recomendaciones`);
  } catch (error) {
    console.error('❌ Error obteniendo recomendaciones:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener recomendaciones',
      mensaje: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

/**
 * GET /
 * Información del servicio
 */
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'DL Service - Identificación de Productos',
    version: '2.0.0',
    description: 'Servicio de identificación de productos mediante imágenes con Deep Learning',
    features: [
      'Identificación de productos por imagen (MobileNet v2)',
      'Predicción de ventas futuras',
      'Recomendación de productos relacionados',
      '46 productos en español del supermercado'
    ],
    endpoints: {
      main: 'POST /api/identificar-producto - Identificar producto completo',
      health: 'GET /health - Estado del servicio',
      productos: 'GET /api/productos - Lista de productos'
    },
    usage: {
      method: 'POST',
      url: '/api/identificar-producto',
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      body: {
        image: '<archivo de imagen>'
      }
    }
  });
});

// ===================================
// MANEJO DE ERRORES
// ===================================

app.use((error: Error, _req: Request, res: Response, _next: any) => {
  console.error('💥 Error no manejado:', error);
  res.status(500).json({
    success: false,
    error: 'Error interno del servidor',
    mensaje: error.message
  });
});

// Ruta no encontrada
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint no encontrado',
    mensaje: `La ruta ${req.method} ${req.path} no existe`,
    endpoints_disponibles: [
      'POST /api/identificar-producto',
      'GET /health',
      'GET /api/productos',
      'GET /'
    ]
  });
});

// ===================================
// INICIO DEL SERVIDOR
// ===================================

const iniciarServidor = async () => {
  try {
    // Pre-cargar modelo MobileNet
    console.log('🚀 Iniciando DL Service...\n');
    console.log('📥 Pre-cargando MobileNet v2...');
    await UnifiedProductService.cargarModelo();
    console.log('✅ Modelo cargado y listo\n');

    // Iniciar servidor
    app.listen(PORT, () => {
      console.log('='.repeat(70));
      console.log('🎉 DL SERVICE - IDENTIFICACIÓN DE PRODUCTOS');
      console.log('='.repeat(70));
      console.log(`🌐 Servidor:        http://localhost:${PORT}`);
      console.log(`💚 Health check:    http://localhost:${PORT}/health`);
      console.log(`📋 Info:            http://localhost:${PORT}/`);
      console.log('');
      console.log('🧠 Modelo:          MobileNet v2 (TensorFlow.js)');
      console.log('📦 Productos:       46 productos en español');
      console.log('🏷️  Categorías:      8 categorías de supermercado');
      console.log('');
      console.log('📡 Endpoint Principal:');
      console.log('   POST /api/identificar-producto');
      console.log('        → Identificación completa por imagen');
      console.log('        → Predicción de ventas');
      console.log('        → Productos relacionados');
      console.log('');
      console.log('📸 Uso desde Frontend:');
      console.log('   - Arrastrar y soltar imagen');
      console.log('   - Seleccionar desde explorador');
      console.log('   - Formato: JPG, PNG, GIF, WEBP');
      console.log('   - Tamaño máximo: 10MB');
      console.log('');
      console.log('✅ Servicio listo para recibir peticiones');
      console.log('='.repeat(70));
      console.log('');
    });
  } catch (error) {
    console.error('❌ Error iniciando servidor:', error);
    process.exit(1);
  }
};

// Manejo de cierre graceful
process.on('SIGTERM', () => {
  console.log('\n🛑 Cerrando servidor...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n🛑 Cerrando servidor...');
  process.exit(0);
});

// Iniciar
iniciarServidor();
