// API client for ML Service
const ML_SERVICE_URL = 'http://localhost:8081';

export interface PredictPriceRequest {
  categoria: string;
  stock: number;
  nombre: string;
}

export interface PredictPriceResponse {
  precio_sugerido: number;
  categoria: string;
  confianza: number;
  features_used: string[];
}

export interface ClienteSegment {
  cliente_id: number;
  nombre: string;
  segmento: 'VIP' | 'Regular' | 'Ocasional';
  total_compras: number;
  frecuencia: number;
  ticket_promedio: number;
}

export interface SegmentacionResponse {
  total_clientes: number;
  vip_count: number;
  regular_count: number;
  ocasional_count: number;
  clientes: ClienteSegment[];
}

export interface Anomalia {
  venta_id: number;
  fecha: string;
  total: number;
  score_anomalia: number;
  razon: string;
}

export interface AnomaliesResponse {
  total_ventas_analizadas: number;
  anomalias_detectadas: number;
  anomalias: Anomalia[];
}

export interface SyncResponse {
  productos_synced: number;
  ventas_synced: number;
  clientes_synced: number;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  core_service_reachable: boolean;
  models_trained: boolean;
  cache_size?: {
    productos: number;
    ventas: number;
    clientes: number;
  };
}

export interface ModelInfo {
  model_name: string;
  trained_at: string;
  accuracy?: number;
  samples_count: number;
  features: string;
}

export interface ModelsResponse {
  total_models: number;
  models: ModelInfo[];
}

class MLServiceAPI {
  private baseURL: string;

  constructor(baseURL: string = ML_SERVICE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`ML Service error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Health check
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // Sync data and train models
  async sync(): Promise<SyncResponse> {
    return this.request<SyncResponse>('/sync', {
      method: 'POST',
    });
  }

  // Predict price (ML Supervisado)
  async predictPrice(data: PredictPriceRequest): Promise<PredictPriceResponse> {
    return this.request<PredictPriceResponse>('/predict/price', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Customer segmentation (ML No Supervisado)
  async getSegmentation(): Promise<SegmentacionResponse> {
    return this.request<SegmentacionResponse>('/ml/segmentacion');
  }

  // Anomaly detection (ML Semi-Supervisado)
  async getAnomalies(): Promise<AnomaliesResponse> {
    return this.request<AnomaliesResponse>('/ml/anomalias');
  }

  // Get models metadata
  async getModels(): Promise<ModelsResponse> {
    return this.request<ModelsResponse>('/models');
  }
}

export const mlAPI = new MLServiceAPI();
