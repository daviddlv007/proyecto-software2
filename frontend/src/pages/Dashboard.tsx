import React, { useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Avatar,
  Grid,
  CircularProgress
} from '@mui/material';
import {
  Category,
  Inventory,
  People,
  ShoppingCart,
  TrendingUp,
  Assignment
} from '@mui/icons-material';
import { useQuery } from '@apollo/client/react';
import {
  GET_ALL_PRODUCTOS,
  GET_ALL_VENTAS,
  GET_ALL_CLIENTES
} from '../graphql/operations';

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip as ReTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
  ScatterChart,
  Scatter
} from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7f50', '#8dd1e1', '#a4de6c', '#d0ed57', '#ffc0cb'];

const Dashboard: React.FC = () => {
  const { data: productosData, loading: loadingProductos } = useQuery(GET_ALL_PRODUCTOS);
  const { data: ventasData, loading: loadingVentas } = useQuery(GET_ALL_VENTAS);
  const { data: clientesData, loading: loadingClientes } = useQuery(GET_ALL_CLIENTES);

  const loading = loadingProductos || loadingVentas || loadingClientes;

  // Compute aggregates using useMemo
  const {
    totalCategorias,
    totalProductos,
    totalClientes,
    ventasHoy,
    ingresosHoy,
    pedidos,
    salesByCategory,
    topProducts,
    salesOverTime,
    customerSegments
  } = useMemo(() => {
    const productos = productosData?.productos || [];
    const ventas = ventasData?.ventas || [];
    const clientes = clientesData?.clientes || [];

    const prodMap: Record<string, any> = {};
    productos.forEach((p: any) => {
      prodMap[p.id] = p;
    });

    // Sales by category
    const byCategory: Record<string, number> = {};

    // Top products (by quantity)
    const prodCounts: Record<string, number> = {};

    // Sales over time (last 30 days)
    const byDate: Record<string, number> = {};

    // Customer metrics
    const customerMetrics: Record<string, { total: number; count: number }> = {};

    ventas.forEach((v: any) => {
      const fechaKey = v.fecha ? v.fecha : (new Date()).toISOString().slice(0,10);
      byDate[fechaKey] = byDate[fechaKey] || 0;
      byDate[fechaKey] += Number(v.total || 0);

      if (v.cliente) {
        const cid = v.cliente.id;
        customerMetrics[cid] = customerMetrics[cid] || { total: 0, count: 0 };
        customerMetrics[cid].total += Number(v.total || 0);
        customerMetrics[cid].count += 1;
      }

      (v.detalles || []).forEach((d: any) => {
        const pid = d.producto?.id;
        const qty = Number(d.cantidad || 0);
        const subtotal = Number(d.subtotal || (d.cantidad * d.precioUnitario) || 0);

        // category
        const categoria = prodMap[pid]?.categoria?.nombre || 'Sin categoría';
        byCategory[categoria] = (byCategory[categoria] || 0) + subtotal;

        // product counts
        prodCounts[d.producto?.nombre || pid] = (prodCounts[d.producto?.nombre || pid] || 0) + qty;
      });
    });

    const salesByCategoryArr = Object.entries(byCategory).map(([name, value]) => ({ name, value }));

    const topProductsArr = Object.entries(prodCounts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Prepare sales over last 30 days
    const today = new Date();
    const dates: string[] = [];
    for (let i = 29; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(today.getDate() - i);
      dates.push(d.toISOString().slice(0, 10));
    }
    const salesOverTimeArr = dates.map(date => ({ date, total: Number(byDate[date] || 0) }));

    const customerSegmentsArr = Object.entries(customerMetrics).map(([cid, m]) => ({
      clienteId: cid,
      total: m.total,
      compras: m.count
    }));

    // Basic stats
    const totalCategorias = new Set(productos.map((p: any) => p.categoria?.id)).size || 0;
    const totalProductos = productos.length;
    const totalClientes = clientes.length;

    // Today's sales
    const todayKey = new Date().toISOString().slice(0,10);
    const ventasHoy = ventas.filter((v: any) => v.fecha && v.fecha.startsWith(todayKey)).length;
    const ingresosHoy = ventas.filter((v: any) => v.fecha && v.fecha.startsWith(todayKey)).reduce((s: number, v: any) => s + Number(v.total || 0), 0);
    const pedidos = ventas.length;

    return {
      totalCategorias,
      totalProductos,
      totalClientes,
      ventasHoy,
      ingresosHoy,
      pedidos,
      salesByCategory: salesByCategoryArr,
      topProducts: topProductsArr,
      salesOverTime: salesOverTimeArr,
      customerSegments: customerSegmentsArr
    };
  }, [productosData, ventasData, clientesData]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        Dashboard - Panel de Control
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Top summary cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {[
              { title: 'Categorías', value: totalCategorias, icon: <Category sx={{ color: '#1976d2' }} /> },
              { title: 'Productos', value: totalProductos, icon: <Inventory sx={{ color: '#388e3c' }} /> },
              { title: 'Clientes', value: totalClientes, icon: <People sx={{ color: '#f57c00' }} /> },
              { title: 'Ventas (total)', value: pedidos, icon: <ShoppingCart sx={{ color: '#7b1fa2' }} /> },
              { title: 'Ingresos Hoy', value: `$${ingresosHoy.toFixed(2)}`, icon: <TrendingUp sx={{ color: '#d32f2f' }} /> },
              { title: 'Pedidos', value: pedidos, icon: <Assignment sx={{ color: '#1976d2' }} /> }
            ].map((s, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Card>
                  <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h5" fontWeight="bold">{s.value}</Typography>
                      <Typography variant="body2" color="text.secondary">{s.title}</Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: 'transparent', width: 56, height: 56 }}>{s.icon}</Avatar>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Charts grid */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2, height: 360 }}>
                <Typography variant="h6" gutterBottom>Ventas por Categoría</Typography>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie dataKey="value" data={salesByCategory} outerRadius={90} label>
                      {salesByCategory.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <ReTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2, height: 360 }}>
                <Typography variant="h6" gutterBottom>Top 10 Productos (unidades)</Typography>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={topProducts} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <ReTooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            <Grid item xs={12} md={12} lg={4}>
              <Paper sx={{ p: 2, height: 360 }}>
                <Typography variant="h6" gutterBottom>Ventas - Últimos 30 días</Typography>
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={salesOverTime} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <ReTooltip />
                    <Line type="monotone" dataKey="total" stroke="#82ca9d" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            <Grid item xs={12} md={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Segmentación de Clientes (Total gastado vs Compras)</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid />
                    <XAxis type="number" dataKey="total" name="Total Gastado" unit="$" />
                    <YAxis type="number" dataKey="compras" name="Compras" />
                    <ReTooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter name="Clientes" data={customerSegments} fill="#8884d8" />
                  </ScatterChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>
        </>
      )}

      {/* Debug Info removido - datos ahora en gráficas reales */}
    </Box>
  );
};

export default Dashboard;