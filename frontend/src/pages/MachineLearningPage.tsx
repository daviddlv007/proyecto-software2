import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
  TextField,
  MenuItem,
  Divider,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Stack,
} from '@mui/material';
import {
  Psychology,
  Group,
  Warning,
  Sync,
  TrendingUp,
  AttachMoney,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  mlAPI,
  type PredictPriceRequest,
  type SegmentacionResponse,
  type AnomaliesResponse,
  type HealthResponse,
} from '../api/mlService';

const COLORS = {
  VIP: '#4caf50',
  Regular: '#2196f3',
  Ocasional: '#ff9800',
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ml-tabpanel-${index}`}
      aria-labelledby={`ml-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const MachineLearningPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // Predicción de Precios (ML Supervisado)
  const [priceForm, setPriceForm] = useState<PredictPriceRequest>({
    categoria: 'Bebidas',
    stock: 50,
    nombre: 'Producto Ejemplo',
  });
  const [pricePrediction, setPricePrediction] = useState<number | null>(null);

  // Segmentación de Clientes (ML No Supervisado)
  const [segmentation, setSegmentation] = useState<SegmentacionResponse | null>(null);

  // Detección de Anomalías (ML Semi-Supervisado)
  const [anomalies, setAnomalies] = useState<AnomaliesResponse | null>(null);

  const categorias = [
    'Lácteos',
    'Bebidas',
    'Panadería',
    'Carnes',
    'Frutas y Verduras',
    'Limpieza',
    'Congelados',
    'Snacks',
    'Abarrotes',
    'Cuidado Personal',
  ];

  // Health check al cargar
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const healthData = await mlAPI.health();
      setHealth(healthData);
      if (!healthData.models_trained) {
        setError('Los modelos ML no están entrenados. Por favor, sincroniza los datos.');
      }
    } catch (err) {
      setError('No se puede conectar con el servicio ML. Verifica que esté corriendo en puerto 8081.');
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    try {
      await mlAPI.sync();
      await checkHealth();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al sincronizar datos');
    } finally {
      setSyncing(false);
    }
  };

  const handlePredictPrice = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await mlAPI.predictPrice(priceForm);
      setPricePrediction(result.precio_sugerido);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al predecir precio');
    } finally {
      setLoading(false);
    }
  };

  const loadSegmentation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await mlAPI.getSegmentation();
      setSegmentation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar segmentación');
    } finally {
      setLoading(false);
    }
  };

  const loadAnomalies = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await mlAPI.getAnomalies();
      setAnomalies(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar anomalías');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError(null);
    setPricePrediction(null);

    // Auto-cargar datos al cambiar de tab
    if (newValue === 1 && !segmentation) {
      loadSegmentation();
    } else if (newValue === 2 && !anomalies) {
      loadAnomalies();
    }
  };

  const getSegmentColor = (segment: string) => {
    return COLORS[segment as keyof typeof COLORS] || '#757575';
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology color="primary" />
            Machine Learning
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Análisis predictivo con 3 tipos de ML: Supervisado, No Supervisado y Semi-Supervisado
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <Sync />}
          onClick={handleSync}
          disabled={syncing}
        >
          {syncing ? 'Sincronizando...' : 'Sincronizar & Entrenar'}
        </Button>
      </Box>

      {/* Health Status */}
      {health && (
        <Alert
          severity={health.models_trained ? 'success' : 'warning'}
          icon={health.models_trained ? <CheckCircle /> : <Warning />}
          sx={{ mb: 3 }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Typography variant="body2">
              <strong>Estado:</strong> {health.status} | 
              <strong> Core Service:</strong> {health.core_service_reachable ? 'Conectado' : 'Desconectado'} |
              <strong> Modelos:</strong> {health.models_trained ? 'Entrenados' : 'No entrenados'}
            </Typography>
            {health.cache_size && (
              <Typography variant="body2" color="text.secondary">
                Cache: {health.cache_size.productos} productos, {health.cache_size.ventas} ventas, {health.cache_size.clientes} clientes
              </Typography>
            )}
          </Box>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Card>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 },
          }}
        >
          <Tab label="Predicción de Precios (Supervisado)" icon={<AttachMoney />} iconPosition="start" />
          <Tab label="Segmentación de Clientes (No Supervisado)" icon={<Group />} iconPosition="start" />
          <Tab label="Detección de Anomalías (Semi-Supervisado)" icon={<Warning />} iconPosition="start" />
        </Tabs>

        {/* Tab 1: Predicción de Precios */}
        <TabPanel value={tabValue} index={0}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Predicción de Precio con Regresión Lineal
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Ingresa las características de un producto para predecir su precio óptimo basado en datos históricos.
            </Typography>

            <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
              <Box sx={{ flex: 1 }}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                    Datos del Producto
                  </Typography>
                  <Stack spacing={2}>
                    <TextField
                      select
                      fullWidth
                      label="Categoría"
                      value={priceForm.categoria}
                      onChange={(e) => setPriceForm({ ...priceForm, categoria: e.target.value })}
                    >
                      {categorias.map((cat) => (
                        <MenuItem key={cat} value={cat}>
                          {cat}
                        </MenuItem>
                      ))}
                    </TextField>
                    <TextField
                      fullWidth
                      label="Nombre del Producto"
                      value={priceForm.nombre}
                      onChange={(e) => setPriceForm({ ...priceForm, nombre: e.target.value })}
                      helperText="El largo del nombre influye en la predicción"
                    />
                    <TextField
                      fullWidth
                      type="number"
                      label="Stock Inicial"
                      value={priceForm.stock}
                      onChange={(e) => setPriceForm({ ...priceForm, stock: parseInt(e.target.value) || 0 })}
                      helperText="Cantidad de unidades disponibles"
                    />
                    <Button
                      fullWidth
                      variant="contained"
                      size="large"
                      startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <TrendingUp />}
                      onClick={handlePredictPrice}
                      disabled={loading || !health?.models_trained}
                    >
                      {loading ? 'Prediciendo...' : 'Predecir Precio'}
                    </Button>
                  </Stack>
                </Paper>
              </Box>

              <Box sx={{ flex: 1 }}>
                <Paper sx={{ p: 3, minHeight: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                  {pricePrediction !== null ? (
                    <>
                      <Typography variant="h3" color="primary" gutterBottom>
                        ${pricePrediction.toFixed(2)}
                      </Typography>
                      <Typography variant="h6" color="text.secondary" gutterBottom>
                        Precio Sugerido
                      </Typography>
                      <Divider sx={{ width: '100%', my: 2 }} />
                      <Box sx={{ width: '100%', textAlign: 'left' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          <strong>Categoría:</strong> {priceForm.categoria}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          <strong>Stock:</strong> {priceForm.stock} unidades
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Producto:</strong> {priceForm.nombre}
                        </Typography>
                      </Box>
                      <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
                        Predicción basada en Regresión Lineal con {health?.cache_size?.productos || 0} productos
                      </Alert>
                    </>
                  ) : (
                    <Box sx={{ textAlign: 'center' }}>
                      <AttachMoney sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                      <Typography variant="body1" color="text.secondary">
                        Completa el formulario y presiona "Predecir Precio" para obtener una sugerencia
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Box>
            </Box>
          </CardContent>
        </TabPanel>

        {/* Tab 2: Segmentación de Clientes */}
        <TabPanel value={tabValue} index={1}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Segmentación de Clientes con K-Means
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Clustering automático en 3 grupos: VIP, Regular y Ocasional
                </Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={loading ? <CircularProgress size={20} /> : <Sync />}
                onClick={loadSegmentation}
                disabled={loading || !health?.models_trained}
              >
                {loading ? 'Cargando...' : 'Actualizar'}
              </Button>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {segmentation && (
              <Stack spacing={3}>
                {/* Summary Cards */}
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#f5f5f5' }}>
                    <CardContent>
                      <Typography variant="h4" color="text.primary">
                        {segmentation.total_clientes}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Clientes
                      </Typography>
                    </CardContent>
                  </Card>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#e8f5e9' }}>
                    <CardContent>
                      <Typography variant="h4" color={COLORS.VIP}>
                        {segmentation.vip_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clientes VIP
                      </Typography>
                    </CardContent>
                  </Card>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#e3f2fd' }}>
                    <CardContent>
                      <Typography variant="h4" color={COLORS.Regular}>
                        {segmentation.regular_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clientes Regulares
                      </Typography>
                    </CardContent>
                  </Card>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#fff3e0' }}>
                    <CardContent>
                      <Typography variant="h4" color={COLORS.Ocasional}>
                        {segmentation.ocasional_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clientes Ocasionales
                      </Typography>
                    </CardContent>
                  </Card>
                </Box>

                {/* Charts */}
                <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' } }}>
                  <Paper sx={{ flex: 1, p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                      Distribución por Segmento
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'VIP', value: segmentation.vip_count },
                            { name: 'Regular', value: segmentation.regular_count },
                            { name: 'Ocasional', value: segmentation.ocasional_count },
                          ]}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => `${entry.name}: ${entry.value}`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {[0, 1, 2].map((index) => (
                            <Cell key={`cell-${index}`} fill={Object.values(COLORS)[index]} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Paper>

                  <Paper sx={{ flex: 1, p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                      Ticket Promedio por Segmento
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={[
                          {
                            segmento: 'VIP',
                            ticket: segmentation.clientes
                              .filter((c) => c.segmento === 'VIP')
                              .reduce((sum, c) => sum + c.ticket_promedio, 0) / segmentation.vip_count || 0,
                          },
                          {
                            segmento: 'Regular',
                            ticket: segmentation.clientes
                              .filter((c) => c.segmento === 'Regular')
                              .reduce((sum, c) => sum + c.ticket_promedio, 0) / segmentation.regular_count || 0,
                          },
                          {
                            segmento: 'Ocasional',
                            ticket: segmentation.clientes
                              .filter((c) => c.segmento === 'Ocasional')
                              .reduce((sum, c) => sum + c.ticket_promedio, 0) / segmentation.ocasional_count || 0,
                          },
                        ]}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="segmento" />
                        <YAxis />
                        <RechartsTooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                        <Bar dataKey="ticket" fill="#8884d8">
                          {[0, 1, 2].map((index) => (
                            <Cell key={`cell-${index}`} fill={Object.values(COLORS)[index]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Box>

                {/* Table */}
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Cliente</TableCell>
                        <TableCell>Segmento</TableCell>
                        <TableCell align="right">Total Compras</TableCell>
                        <TableCell align="right">Frecuencia</TableCell>
                        <TableCell align="right">Ticket Promedio</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {segmentation.clientes
                        .sort((a, b) => b.total_compras - a.total_compras)
                        .slice(0, 10)
                        .map((cliente) => (
                          <TableRow key={cliente.cliente_id} hover>
                            <TableCell>{cliente.nombre}</TableCell>
                            <TableCell>
                              <Chip
                                label={cliente.segmento}
                                size="small"
                                sx={{
                                  bgcolor: getSegmentColor(cliente.segmento),
                                  color: 'white',
                                  fontWeight: 600,
                                }}
                              />
                            </TableCell>
                            <TableCell align="right">${cliente.total_compras.toFixed(2)}</TableCell>
                            <TableCell align="right">{cliente.frecuencia} compras</TableCell>
                            <TableCell align="right">${cliente.ticket_promedio.toFixed(2)}</TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {segmentation.clientes.length > 10 && (
                  <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
                    Mostrando top 10 de {segmentation.clientes.length} clientes
                  </Typography>
                )}
              </Stack>
            )}

            {!loading && !segmentation && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Group sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Presiona "Actualizar" para cargar la segmentación de clientes
                </Typography>
              </Box>
            )}
          </CardContent>
        </TabPanel>

        {/* Tab 3: Detección de Anomalías */}
        <TabPanel value={tabValue} index={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Detección de Anomalías con Isolation Forest
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Identifica ventas inusuales que podrían indicar fraudes o errores
                </Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={loading ? <CircularProgress size={20} /> : <Sync />}
                onClick={loadAnomalies}
                disabled={loading || !health?.models_trained}
              >
                {loading ? 'Cargando...' : 'Actualizar'}
              </Button>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {anomalies && (
              <Stack spacing={3}>
                {/* Summary */}
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#f5f5f5' }}>
                    <CardContent>
                      <Typography variant="h4" color="text.primary">
                        {anomalies.total_ventas_analizadas}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Ventas Analizadas
                      </Typography>
                    </CardContent>
                  </Card>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#fff3e0' }}>
                    <CardContent>
                      <Typography variant="h4" color="warning.main">
                        {anomalies.anomalias_detectadas}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Anomalías Detectadas
                      </Typography>
                    </CardContent>
                  </Card>
                  <Card sx={{ flex: '1 1 200px', bgcolor: '#e8f5e9' }}>
                    <CardContent>
                      <Typography variant="h4" color="success.main">
                        {((anomalies.anomalias_detectadas / anomalies.total_ventas_analizadas) * 100).toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Tasa de Anomalías
                      </Typography>
                    </CardContent>
                  </Card>
                </Box>

                {/* Anomalies Table */}
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Venta ID</TableCell>
                        <TableCell>Fecha</TableCell>
                        <TableCell align="right">Total</TableCell>
                        <TableCell align="right">Score Anomalía</TableCell>
                        <TableCell>Razón</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {anomalies.anomalias.map((anomalia) => (
                        <TableRow key={anomalia.venta_id} hover>
                          <TableCell>
                            <Chip
                              icon={<ErrorIcon />}
                              label={`#${anomalia.venta_id}`}
                              size="small"
                              color="warning"
                            />
                          </TableCell>
                          <TableCell>{new Date(anomalia.fecha).toLocaleDateString()}</TableCell>
                          <TableCell align="right">
                            <Typography fontWeight={600}>${anomalia.total.toFixed(2)}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={anomalia.score_anomalia.toFixed(3)}
                              size="small"
                              color={anomalia.score_anomalia < -0.3 ? 'error' : 'warning'}
                            />
                          </TableCell>
                          <TableCell>{anomalia.razon}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {anomalies.anomalias.length === 0 && (
                  <Alert severity="success">
                    <Typography variant="body2">
                      ¡Excelente! No se detectaron anomalías significativas en las ventas.
                    </Typography>
                  </Alert>
                )}
              </Stack>
            )}

            {!loading && !anomalies && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Warning sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Presiona "Actualizar" para detectar anomalías en las ventas
                </Typography>
              </Box>
            )}
          </CardContent>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default MachineLearningPage;
