// API client for DL Service (Deep Learning)
const DL_SERVICE_URL = 'http://localhost:8082';

// ==========================================
// TIPOS DE RESPUESTA
// ==========================================

export interface ProductoIdentificado {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  stock: number;
  keywords_mobilenet: string[];
  confianza: number;
}

export interface PrediccionVentas {
  proximos_7_dias: number[];
  tendencia: 'creciente' | 'estable' | 'decreciente';
  promedio_diario: number;
  confianza?: number;
  metodo?: 'LSTM' | 'Simulado';
}

export interface ProductoRelacionado {
  id: number;
  nombre: string;
  categoria: string;
  score_relacion: number;
  razon: string;
}

export interface PrediccionRaw {
  clase_mobilenet: string;
  probabilidad: number;
}

export interface IdentificarProductoResponse {
  success: boolean;
  producto?: ProductoIdentificado;
  prediccion_ventas?: PrediccionVentas;
  productos_relacionados?: ProductoRelacionado[];
  predicciones_raw?: PrediccionRaw[];
  mensaje: string;
  imagen_url?: string;
  timestamp?: string;
  error?: string;
}

export interface ProductoDisponible {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  stock: number;
  keywords_mobilenet: string[];
}

export interface ProductosListResponse {
  total: number;
  categorias: string[];
  productos: ProductoDisponible[];
}

export interface DLHealthResponse {
  status: string;
  service: string;
  timestamp: string;
  modelo: string;
  endpoints: {
    identificar: string;
  };
}

// ==========================================
// API METHODS
// ==========================================

class DLService {
  private baseUrl: string;

  constructor(baseUrl: string = DL_SERVICE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Health check del servicio
   */
  async health(): Promise<DLHealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Identificar producto por imagen
   */
  async identificarProducto(imageFile: File): Promise<IdentificarProductoResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${this.baseUrl}/api/identificar-producto`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error al identificar producto: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Obtener lista de productos disponibles
   */
  async getProductos(): Promise<ProductosListResponse> {
    const response = await fetch(`${this.baseUrl}/api/productos`);
    if (!response.ok) {
      throw new Error(`Error al obtener productos: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Buscar producto por nombre (case insensitive, sin acentos)
   */
  async buscarProductoPorNombre(nombre: string): Promise<ProductoDisponible | null> {
    const productosResponse = await this.getProductos();
    const nombreNormalizado = this.normalizarTexto(nombre);
    
    const producto = productosResponse.productos.find(p => 
      this.normalizarTexto(p.nombre).includes(nombreNormalizado)
    );
    
    return producto || null;
  }

  /**
   * Normalizar texto: sin acentos, minúsculas, sin espacios extras
   */
  private normalizarTexto(texto: string): string {
    return texto
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Quitar acentos
      .trim();
  }

  /**
   * Sincronizar datos con Core Service
   */
  async sync(): Promise<{ success: boolean; mensaje: string; detalles?: any }> {
    const response = await fetch(`${this.baseUrl}/api/sync`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Error al sincronizar: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Entrenar sistema de recomendaciones con Deep Learning
   */
  async train(): Promise<{ success: boolean; mensaje: string; detalles?: any }> {
    const response = await fetch(`${this.baseUrl}/api/train`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Error al entrenar: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// Export singleton instance
export const dlAPI = new DLService();

// Export class for custom instances
export default DLService;
