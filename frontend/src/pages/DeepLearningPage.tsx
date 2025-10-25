import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  TextField,
  MenuItem,
  Divider,
  Paper,
  Stack,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  CloudUpload,
  ImageSearch,
  Mic,
  MicOff,
  CheckCircle,
  Error as ErrorIcon,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Inventory,
  AttachMoney,
  Category,
  LocalShipping,
  Recommend,
  Sync,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import {
  dlAPI,
  type IdentificarProductoResponse,
  type ProductoDisponible,
} from '../api/dlService';

// Definir el tipo de la API de reconocimiento de voz
interface SpeechRecognitionEvent extends Event {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: (() => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

const DeepLearningPage: React.FC = () => {
  // Estados principales
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<IdentificarProductoResponse | null>(null);
  const [syncStatus, setSyncStatus] = useState<string | null>(null);
  const [trainStatus, setTrainStatus] = useState<string | null>(null);
  
  // Estados para entrada de imagen
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  
  // Estados para selector de productos
  const [productos, setProductos] = useState<ProductoDisponible[]>([]);
  const [productoSeleccionado, setProductoSeleccionado] = useState<string>('');
  
  // Estados para reconocimiento de voz
  const [escuchando, setEscuchando] = useState(false);
  const [transcripcion, setTranscripcion] = useState('');
  const [soportaVoz, setSoportaVoz] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Inicializar: cargar productos y verificar soporte de voz
  useEffect(() => {
    cargarProductos();
    verificarSoporteVoz();
  }, []);

  const cargarProductos = async () => {
    try {
      const response = await dlAPI.getProductos();
      setProductos(response.productos);
    } catch (err) {
      console.error('Error cargando productos:', err);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    setSyncStatus(null);
    
    try {
      const result = await dlAPI.sync();
      setSyncStatus(result.mensaje);
      
      // Recargar productos después de sincronizar
      await cargarProductos();
      
      console.log('✅ Sincronización completada:', result.detalles);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al sincronizar con Core Service');
    } finally {
      setSyncing(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    setTrainStatus(null);
    
    try {
      const result = await dlAPI.train();
      setTrainStatus(result.mensaje);
      
      console.log('✅ Entrenamiento completado:', result.detalles);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al entrenar modelo de recomendaciones');
    } finally {
      setTraining(false);
    }
  };

  const verificarSoporteVoz = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSoportaVoz(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'es-ES';

      recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        setTranscripcion(transcript);
        buscarProductoPorVoz(transcript);
      };

      recognitionRef.current.onerror = () => {
        setError('Error en el reconocimiento de voz');
        setEscuchando(false);
      };

      recognitionRef.current.onend = () => {
        setEscuchando(false);
      };
    }
  };

  // ==========================================
  // MÉTODO 1: DRAG & DROP / FILE UPLOAD
  // ==========================================

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Por favor selecciona una imagen válida (JPG, PNG, GIF, WEBP)');
      return;
    }

    // Preview de la imagen
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Enviar a identificar
    identificarImagen(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const identificarImagen = async (file: File) => {
    setLoading(true);
    setError(null);
    setResultado(null);

    try {
      console.log('🔍 Identificando producto desde imagen...');
      const response = await dlAPI.identificarProducto(file);
      setResultado(response);
      
      if (!response.success) {
        setError(response.mensaje || 'No se pudo identificar el producto');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al identificar producto');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // MÉTODO 2: SELECTOR DROPDOWN
  // ==========================================

  const handleProductoChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const nombreProducto = e.target.value;
    setProductoSeleccionado(nombreProducto);

    if (!nombreProducto) {
      setResultado(null);
      setImagePreview(null);
      return;
    }

    // Simular resultado para producto seleccionado
    await simularIdentificacionDirecta(nombreProducto);
  };

  const simularIdentificacionDirecta = async (nombreProducto: string) => {
    setLoading(true);
    setError(null);

    try {
      const producto = productos?.find(p => p.nombre === nombreProducto);
      if (!producto) {
        setError('Producto no encontrado');
        setLoading(false);
        return;
      }

      // Simular predicción de ventas
      const prediccionVentas = {
        proximos_7_dias: Array.from({ length: 7 }, () => Math.floor(Math.random() * 20) + 10),
        tendencia: ['creciente', 'estable', 'decreciente'][Math.floor(Math.random() * 3)] as 'creciente' | 'estable' | 'decreciente',
        promedio_diario: Math.floor(Math.random() * 15) + 10
      };

      // Simular productos relacionados
      const relacionados = productos
        ?.filter(p => p.categoria === producto.categoria && p.id !== producto.id)
        .slice(0, 4)
        .map(p => ({
          id: p.id,
          nombre: p.nombre,
          categoria: p.categoria,
          score_relacion: 0.85,
          razon: 'Misma categoría'
        })) || [];

      setResultado({
        success: true,
        producto: {
          ...producto,
          confianza: 1.0
        },
        prediccion_ventas: prediccionVentas,
        productos_relacionados: relacionados,
        mensaje: `✅ Producto seleccionado: ${producto.nombre}`,
        timestamp: new Date().toISOString()
      });

      // Limpiar preview de imagen
      setImagePreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al procesar producto');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // MÉTODO 3: RECONOCIMIENTO DE VOZ
  // ==========================================

  const toggleVoz = () => {
    if (!soportaVoz || !recognitionRef.current) {
      setError('Tu navegador no soporta reconocimiento de voz');
      return;
    }

    if (escuchando) {
      recognitionRef.current.stop();
      setEscuchando(false);
    } else {
      setTranscripcion('');
      setError(null);
      recognitionRef.current.start();
      setEscuchando(true);
    }
  };

  const buscarProductoPorVoz = async (texto: string) => {
    console.log('🎤 Buscando producto por voz:', texto);
    setLoading(true);
    setError(null);
    
    try {
      const producto = await dlAPI.buscarProductoPorNombre(texto);
      
      if (producto) {
        console.log('✅ Producto encontrado:', producto.nombre);
        setProductoSeleccionado(producto.nombre);
        
        // Generar resultados directamente con el producto encontrado
        await simularIdentificacionConProducto(producto);
      } else {
        setError(`No se encontró ningún producto con el nombre "${texto}"`);
        setLoading(false);
      }
    } catch (err) {
      setError('Error al buscar producto por voz');
      setLoading(false);
    }
  };

  const simularIdentificacionConProducto = async (producto: ProductoDisponible) => {
    // Simular predicción de ventas
    const prediccionVentas = {
      proximos_7_dias: Array.from({ length: 7 }, () => Math.floor(Math.random() * 20) + 10),
      tendencia: ['creciente', 'estable', 'decreciente'][Math.floor(Math.random() * 3)] as 'creciente' | 'estable' | 'decreciente',
      promedio_diario: Math.floor(Math.random() * 15) + 10
    };

    // Obtener productos relacionados - obtener del API si el estado local está vacío
    let productosParaBusqueda = productos;
    if (!productosParaBusqueda || productosParaBusqueda.length === 0) {
      try {
        const response = await dlAPI.getProductos();
        productosParaBusqueda = response.productos;
        setProductos(response.productos); // Actualizar el estado también
      } catch (err) {
        console.error('Error cargando productos para relacionados:', err);
        productosParaBusqueda = [];
      }
    }

    const relacionados = productosParaBusqueda
      .filter(p => p.categoria === producto.categoria && p.id !== producto.id)
      .slice(0, 4)
      .map(p => ({
        id: p.id,
        nombre: p.nombre,
        categoria: p.categoria,
        score_relacion: 0.85,
        razon: 'Misma categoría'
      }));

    console.log('📦 Productos relacionados encontrados:', relacionados.length);

    setResultado({
      success: true,
      producto: {
        ...producto,
        confianza: 1.0
      },
      prediccion_ventas: prediccionVentas,
      productos_relacionados: relacionados,
      mensaje: `✅ Producto identificado por voz: ${producto.nombre}`,
      timestamp: new Date().toISOString()
    });

    setLoading(false);
    setImagePreview(null);
  };

  // ==========================================
  // RENDERIZADO
  // ==========================================

  const getTendenciaIcon = (tendencia?: string) => {
    switch (tendencia) {
      case 'creciente': return <TrendingUp color="success" />;
      case 'decreciente': return <TrendingDown color="error" />;
      default: return <TrendingFlat color="info" />;
    }
  };

  const formatChartData = (ventas?: number[]) => {
    if (!ventas) return [];
    return ventas.map((cantidad, index) => ({
      dia: `Día ${index + 1}`,
      cantidad
    }));
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ImageSearch color="primary" />
            Deep Learning - Identificación de Productos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Identifica productos usando imagen, selector o voz. Obtén predicciones de ventas y recomendaciones.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <Sync />}
            onClick={handleSync}
            disabled={syncing || training}
          >
            {syncing ? 'Sincronizando...' : 'Sincronizar Datos'}
          </Button>
          <Button
            variant="contained"
            color="secondary"
            startIcon={training ? <CircularProgress size={20} color="inherit" /> : <SmartToyIcon />}
            onClick={handleTrain}
            disabled={syncing || training}
          >
            {training ? 'Entrenando...' : 'Entrenar Recomendaciones'}
          </Button>
        </Box>
      </Box>

      {/* Sync Status */}
      {syncStatus && (
        <Alert severity="success" onClose={() => setSyncStatus(null)} sx={{ mb: 3 }}>
          {syncStatus} - {productos.length} productos disponibles
        </Alert>
      )}

      {/* Train Status */}
      {trainStatus && (
        <Alert severity="success" onClose={() => setTrainStatus(null)} sx={{ mb: 3 }}>
          <strong>🧠 Modelo Entrenado:</strong> {trainStatus}
          <br />
          <Typography variant="caption" component="div" sx={{ mt: 1 }}>
            • Método: Autoencoder + Product Embeddings (Deep Learning)
            <br />
            • Dimensiones: 32 (compresión inteligente de relaciones)
            <br />
            • Técnica: Collaborative Filtering basado en co-compra
          </Typography>
        </Alert>
      )}

      {/* Status Info */}
      <Alert severity="info" icon={<CheckCircle />} sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Typography variant="body2">
            <strong>Estado:</strong> Servicio Activo |
            <strong> Modelo:</strong> MobileNet v2 |
            <strong> Productos:</strong> {productos.length} disponibles |
            <strong> Categorías:</strong> 8
          </Typography>
        </Box>
      </Alert>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Métodos de Entrada */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Método 1: Drag & Drop */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CloudUpload color="primary" />
                Método 1: Imagen
              </Typography>
              
              <Paper
                sx={{
                  border: '2px dashed',
                  borderColor: dragOver ? 'primary.main' : 'grey.400',
                  bgcolor: dragOver ? 'action.hover' : 'background.paper',
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover'
                  }
                }}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileInputChange}
                  style={{ display: 'none' }}
                />
                
                {imagePreview ? (
                  <img
                    src={imagePreview}
                    alt="Preview"
                    style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8 }}
                  />
                ) : (
                  <>
                    <CloudUpload sx={{ fontSize: 60, color: 'text.disabled', mb: 1 }} />
                    <Typography variant="body1" gutterBottom>
                      Arrastra una imagen aquí
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      o haz clic para seleccionar
                    </Typography>
                  </>
                )}
              </Paper>

              {imagePreview && (
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 2 }}
                  onClick={() => {
                    setImagePreview(null);
                    setResultado(null);
                  }}
                >
                  Limpiar
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Método 2: Selector */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Inventory color="primary" />
                Método 2: Selector
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Selecciona un producto del catálogo
              </Typography>

              <TextField
                select
                fullWidth
                label="Seleccionar Producto"
                value={productoSeleccionado}
                onChange={handleProductoChange}
                disabled={loading}
                helperText={`${productos?.length || 0} productos disponibles`}
              >
                <MenuItem value="">
                  <em>Ninguno</em>
                </MenuItem>
                {productos?.map((producto) => (
                  <MenuItem key={producto.id} value={producto.nombre}>
                    {producto.nombre}
                  </MenuItem>
                ))}
              </TextField>

              {productoSeleccionado && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Producto seleccionado: <strong>{productoSeleccionado}</strong>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Método 3: Voz */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Mic color="primary" />
                Método 3: Voz
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Di el nombre del producto
              </Typography>

              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Tooltip title={soportaVoz ? (escuchando ? 'Detener' : 'Activar micrófono') : 'No soportado'}>
                  <span>
                    <IconButton
                      color={escuchando ? 'error' : 'primary'}
                      onClick={toggleVoz}
                      disabled={!soportaVoz}
                      sx={{
                        width: 80,
                        height: 80,
                        border: '3px solid',
                        borderColor: escuchando ? 'error.main' : 'primary.main',
                        animation: escuchando ? 'pulse 1.5s infinite' : 'none',
                        '@keyframes pulse': {
                          '0%': { transform: 'scale(1)', opacity: 1 },
                          '50%': { transform: 'scale(1.05)', opacity: 0.8 },
                          '100%': { transform: 'scale(1)', opacity: 1 }
                        }
                      }}
                    >
                      {escuchando ? <MicOff sx={{ fontSize: 40 }} /> : <Mic sx={{ fontSize: 40 }} />}
                    </IconButton>
                  </span>
                </Tooltip>

                {escuchando && (
                  <Typography variant="body2" color="error" sx={{ mt: 2, fontWeight: 'bold' }}>
                    🎤 Escuchando... Habla ahora
                  </Typography>
                )}

                {!escuchando && transcripcion && loading && (
                  <Typography variant="body2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                    🔍 Buscando producto...
                  </Typography>
                )}

                {transcripcion && !loading && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    Escuchado: <strong>"{transcripcion}"</strong>
                  </Alert>
                )}

                {!soportaVoz && (
                  <Alert severity="warning" sx={{ mt: 2 }}>
                    Tu navegador no soporta reconocimiento de voz
                  </Alert>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading */}
      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
            Identificando producto...
          </Typography>
        </Box>
      )}

      {/* Resultados */}
      {resultado && resultado.success && resultado.producto && (
        <Grid container spacing={3}>
          {/* Producto Identificado */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  Producto Identificado
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="h4" gutterBottom>
                    {resultado.producto.nombre}
                  </Typography>

                  <Stack spacing={2} sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Category color="action" />
                        <Typography variant="body2" color="text.secondary">Categoría:</Typography>
                      </Box>
                      <Chip label={resultado.producto.categoria} color="primary" size="small" />
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AttachMoney color="action" />
                        <Typography variant="body2" color="text.secondary">Precio:</Typography>
                      </Box>
                      <Typography variant="h6" color="primary">
                        ${resultado.producto.precio.toFixed(2)}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LocalShipping color="action" />
                        <Typography variant="body2" color="text.secondary">Stock:</Typography>
                      </Box>
                      <Typography variant="body1">
                        {resultado.producto.stock} unidades
                      </Typography>
                    </Box>

                    <Divider />

                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Confianza de Identificación:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={resultado.producto.confianza * 100}
                          sx={{ flex: 1, height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="body2" fontWeight="bold">
                          {(resultado.producto.confianza * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>
                  </Stack>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Predicción de Ventas */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUp color="primary" />
                  Predicción de Ventas (7 días)
                </Typography>

                {resultado.prediccion_ventas && (
                  <>
                    <Box sx={{ display: 'flex', gap: 2, my: 2, flexWrap: 'wrap' }}>
                      <Chip
                        icon={getTendenciaIcon(resultado.prediccion_ventas.tendencia)}
                        label={`Tendencia: ${resultado.prediccion_ventas.tendencia}`}
                        color={
                          resultado.prediccion_ventas.tendencia === 'creciente' ? 'success' :
                          resultado.prediccion_ventas.tendencia === 'decreciente' ? 'error' : 'info'
                        }
                      />
                      <Chip
                        label={`Promedio: ${resultado.prediccion_ventas.promedio_diario} un/día`}
                        variant="outlined"
                      />
                      {resultado.prediccion_ventas.metodo && (
                        <Chip
                          label={`Método: ${resultado.prediccion_ventas.metodo}${
                            resultado.prediccion_ventas.metodo === 'LSTM' && resultado.prediccion_ventas.confianza 
                              ? ` (${(resultado.prediccion_ventas.confianza * 100).toFixed(0)}%)` 
                              : ''
                          }`}
                          color={resultado.prediccion_ventas.metodo === 'LSTM' ? 'primary' : 'default'}
                          size="small"
                        />
                      )}
                    </Box>

                    {resultado.prediccion_ventas.metodo === 'LSTM' && (
                      <Alert severity="success" sx={{ mb: 2 }}>
                        🧠 Predicción generada con Deep Learning (LSTM) usando datos históricos reales
                      </Alert>
                    )}

                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={formatChartData(resultado.prediccion_ventas.proximos_7_dias)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="dia" />
                        <YAxis />
                        <RechartsTooltip />
                        <Line
                          type="monotone"
                          dataKey="cantidad"
                          stroke="#1976d2"
                          strokeWidth={2}
                          dot={{ fill: '#1976d2', r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>

                    <TableContainer sx={{ mt: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            {resultado.prediccion_ventas.proximos_7_dias.map((_, i) => (
                              <TableCell key={i} align="center">D{i + 1}</TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          <TableRow>
                            {resultado.prediccion_ventas.proximos_7_dias.map((cantidad, i) => (
                              <TableCell key={i} align="center">
                                <strong>{cantidad}</strong>
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Productos Relacionados */}
          {resultado.productos_relacionados && resultado.productos_relacionados.length > 0 && (
            <Grid size={{ xs: 12 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Recommend color="primary" />
                    Productos Relacionados
                  </Typography>

                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    {resultado.productos_relacionados.map((prod) => (
                      <Grid size={{ xs: 12, sm: 6, md: 3 }} key={prod.id}>
                        <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                              {prod.nombre}
                            </Typography>
                            <Chip label={prod.categoria} size="small" sx={{ mb: 1 }} />
                            <Typography variant="body2" color="text.secondary">
                              {prod.razon}
                            </Typography>
                          </Box>
                          <Box sx={{ mt: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={prod.score_relacion * 100}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              Relación: {(prod.score_relacion * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Predicciones Raw (MobileNet) */}
          {resultado.predicciones_raw && resultado.predicciones_raw.length > 0 && (
            <Grid size={{ xs: 12 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Predicciones MobileNet (Top 5)
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Clase</TableCell>
                          <TableCell align="right">Probabilidad</TableCell>
                          <TableCell align="right">Confianza</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {resultado.predicciones_raw.map((pred, i) => (
                          <TableRow key={i}>
                            <TableCell>{pred.clase_mobilenet}</TableCell>
                            <TableCell align="right">
                              <LinearProgress
                                variant="determinate"
                                value={pred.probabilidad * 100}
                                sx={{ width: 100, display: 'inline-block' }}
                              />
                            </TableCell>
                            <TableCell align="right">{(pred.probabilidad * 100).toFixed(2)}%</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* Sin Resultados */}
      {resultado && !resultado.success && (
        <Alert severity="warning" icon={<ErrorIcon />}>
          {resultado.mensaje}
        </Alert>
      )}
    </Box>
  );
};

export default DeepLearningPage;
