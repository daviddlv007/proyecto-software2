import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client/react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Box,
  Typography,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  CircularProgress
} from '@mui/material';
import { 
  Edit, 
  Delete, 
  Add, 
  Visibility, 
  AddShoppingCart,
  RemoveShoppingCart 
} from '@mui/icons-material';
import { 
  GET_ALL_VENTAS, 
  CREATE_VENTA, 
  UPDATE_VENTA, 
  DELETE_VENTA
} from '../graphql/operations';
import { useReferenceData, formatReferenceOptions } from '../hooks/useReferenceData';
import type { CrudConfig, FormData } from '../types';

interface VentasCrudProps {
  config: CrudConfig;
}

const VentasCrud: React.FC<VentasCrudProps> = ({ }) => {
  // ALL HOOKS MUST BE AT THE TOP - NO CONDITIONAL LOGIC BEFORE HOOKS
  // Reference data hooks
  const { clientes, productos, loading: referencesLoading } = useReferenceData({ 
    loadClientes: true, 
    loadProductos: true 
  });
  
  // State hooks
  const [open, setOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<any>(null);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [viewingItem, setViewingItem] = useState<any>(null);
  const [formData, setFormData] = useState<FormData>({});
  const [detalles, setDetalles] = useState<any[]>([]);
  const [error, setError] = useState('');

  // GraphQL queries - must be called before any early returns
  const { data: ventasData, refetch } = useQuery(GET_ALL_VENTAS);

  // GraphQL mutations - must be called before any early returns
  const [createVenta] = useMutation(CREATE_VENTA, {
    onCompleted: () => {
      setOpen(false);
      setFormData({});
      setDetalles([]);
      refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  const [updateVenta] = useMutation(UPDATE_VENTA, {
    onCompleted: () => {
      setOpen(false);
      setFormData({});
      setDetalles([]);
      setEditingItem(null);
      refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  const [deleteVenta] = useMutation(DELETE_VENTA, {
    onCompleted: () => {
      setConfirmDeleteOpen(false);
      setItemToDelete(null);
      refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  // NOW we can do conditional rendering after all hooks are called
  if (referencesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Cargando datos de referencia...
        </Typography>
      </Box>
    );
  }

  // Extract data from GraphQL responses
  const ventas = ventasData?.ventas || [];

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({ fecha: new Date().toISOString().split('T')[0] });
    setDetalles([]);
    setOpen(true);
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    
    // Convertir la fecha del formato del backend (puede ser "2025-10-23" o "2025-10-23T00:00:00") 
    // al formato requerido por el input date (yyyy-MM-dd)
    let fechaFormateada = item.fecha;
    if (fechaFormateada && fechaFormateada.includes('T')) {
      fechaFormateada = fechaFormateada.split('T')[0];
    }
    
    setFormData({
      clienteId: item.cliente?.id || item.clienteId,
      fecha: fechaFormateada,
      total: item.total
    });
    // Asegurarse de que detalles sea un array, incluso si viene undefined o null
    const detallesArray = Array.isArray(item.detalles) ? item.detalles : [];
    setDetalles(detallesArray.map((detalle: any) => ({
      id: detalle.id || Date.now().toString(),
      productoId: detalle.producto?.id || detalle.productoId,
      producto: detalle.producto,
      cantidad: detalle.cantidad,
      precioUnitario: detalle.precioUnitario
    })));
    setOpen(true);
  };

  const handleDelete = (item: any) => {
    setItemToDelete(item);
    setConfirmDeleteOpen(true);
  };

  const confirmDelete = async () => {
    if (itemToDelete) {
      try {
        await deleteVenta({ variables: { id: itemToDelete.id } });
      } catch (err) {
        console.error('Error deleting venta:', err);
      }
    }
  };

  const handleViewDetails = (item: any) => {
    setViewingItem(item);
    setDetailsOpen(true);
  };

  const handleSave = async () => {
    if (!formData.clienteId || detalles.length === 0) {
      setError('Debe seleccionar un cliente y agregar al menos un producto');
      return;
    }

    // Preparar los detalles en el formato correcto para la API
    const detallesInput = detalles.map(detalle => ({
      productoId: detalle.productoId,
      cantidad: parseInt(detalle.cantidad.toString()),
      precioUnitario: parseFloat(detalle.precioUnitario.toString())
    }));

    // Asegurar que la fecha esté en formato yyyy-MM-dd (sin hora)
    let fechaFormatted = formData.fecha || new Date().toISOString().split('T')[0];
    if (fechaFormatted.includes('T')) {
      fechaFormatted = fechaFormatted.split('T')[0];
    }

    // Preparar el input de la venta (sin total, se calcula automáticamente)
    const ventaInput = {
      clienteId: formData.clienteId,
      fecha: fechaFormatted,
      detalles: detallesInput
    };

    try {
      if (editingItem) {
        console.log('Actualizando venta:', { id: editingItem.id, input: ventaInput });
        await updateVenta({ 
          variables: { 
            id: editingItem.id, 
            input: ventaInput
          } 
        });
      } else {
        console.log('Creando venta:', { input: ventaInput });
        await createVenta({ 
          variables: { 
            input: ventaInput
          } 
        });
      }
      
      console.log('Operación exitosa');
    } catch (err) {
      console.error('Error saving venta:', err);
      setError('Error al guardar la venta. Revisa la consola para más detalles.');
    }
  };

  const handleAddDetalle = () => {
    const newDetalle = {
      id: Date.now().toString(),
      productoId: '',
      producto: null,
      cantidad: 1,
      precioUnitario: 0
    };
    setDetalles(prev => [...prev, newDetalle]);
  };

  const handleUpdateDetalle = (index: number, field: string, value: any) => {
    const newDetalles = [...detalles];
    newDetalles[index][field] = value;

    if (field === 'productoId' && value) {
      const producto = productos.find((p: any) => p.id === value);
      if (producto) {
        newDetalles[index].producto = producto;
        newDetalles[index].precioUnitario = producto.precio;
      }
    }

    setDetalles(newDetalles);
  };

  const handleRemoveDetalle = (index: number) => {
    setDetalles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Ventas</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreate}
        >
          Nueva Venta
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Cliente</TableCell>
              <TableCell>Fecha</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ventas.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.cliente?.nombre}</TableCell>
                <TableCell>{item.fecha}</TableCell>
                <TableCell>${item.total?.toFixed(2)}</TableCell>
                <TableCell>
                  <IconButton 
                    onClick={() => handleViewDetails(item)} 
                    color="info"
                    title="Ver detalles"
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton onClick={() => handleEdit(item)} color="primary">
                    <Edit />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(item)} color="error">
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog para crear/editar venta */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingItem ? 'Editar Venta' : 'Nueva Venta'}
        </DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Cliente</InputLabel>
            <Select
              value={formData.clienteId || ''}
              label="Cliente"
              onChange={(e) => setFormData(prev => ({ ...prev, clienteId: e.target.value }))}
              required
            >
              {clientes.map((cliente: any) => (
                <MenuItem key={cliente.id} value={cliente.id}>
                  {cliente.nombre}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            margin="normal"
            fullWidth
            label="Fecha"
            type="date"
            value={formData.fecha || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, fecha: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />

          <Box sx={{ mt: 3, mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Productos</Typography>
              <Button
                variant="outlined"
                startIcon={<AddShoppingCart />}
                onClick={handleAddDetalle}
              >
                Agregar Producto
              </Button>
            </Box>

            {detalles.map((detalle, index) => (
              <Paper key={detalle.id} elevation={1} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" gap={2} alignItems="center">
                  <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>Producto</InputLabel>
                    <Select
                      value={detalle.productoId || ''}
                      label="Producto"
                      onChange={(e) => handleUpdateDetalle(index, 'productoId', e.target.value)}
                    >
                      {productos.map((producto: any) => (
                        <MenuItem key={producto.id} value={producto.id}>
                          {producto.nombre}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <TextField
                    label="Cantidad"
                    type="number"
                    value={detalle.cantidad}
                    onChange={(e) => handleUpdateDetalle(index, 'cantidad', parseInt(e.target.value) || 1)}
                    sx={{ width: 100 }}
                  />
                  
                  <TextField
                    label="Precio Unitario"
                    type="number"
                    value={detalle.precioUnitario}
                    onChange={(e) => handleUpdateDetalle(index, 'precioUnitario', parseFloat(e.target.value) || 0)}
                    sx={{ width: 120 }}
                  />

                  <Typography variant="body2" sx={{ minWidth: 80 }}>
                    Total: ${((detalle.cantidad || 0) * (detalle.precioUnitario || 0)).toFixed(2)}
                  </Typography>

                  <IconButton 
                    onClick={() => handleRemoveDetalle(index)} 
                    color="error"
                    size="small"
                  >
                    <RemoveShoppingCart />
                  </IconButton>
                </Box>
              </Paper>
            ))}

            {detalles.length > 0 && (
              <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                <Typography variant="h6">
                  Total de la Venta: ${detalles.reduce((sum, detalle) => 
                    sum + ((detalle.cantidad || 0) * (detalle.precioUnitario || 0)), 0
                  ).toFixed(2)}
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancelar</Button>
          <Button onClick={handleSave} variant="contained">
            {editingItem ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para ver detalles */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Detalles de la Venta
        </DialogTitle>
        <DialogContent>
          {viewingItem && (
            <>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Información General
                </Typography>
                <Typography><strong>Cliente:</strong> {viewingItem.cliente?.nombre}</Typography>
                <Typography><strong>Fecha:</strong> {viewingItem.fecha}</Typography>
                <Typography><strong>Total:</strong> ${viewingItem.total?.toFixed(2)}</Typography>
              </Box>

              <Typography variant="h6" gutterBottom>
                Productos
              </Typography>
              <List>
                {viewingItem.detalles?.map((detalle: any, index: number) => (
                  <React.Fragment key={detalle.id}>
                    <ListItem>
                      <ListItemText
                        primary={detalle.producto?.nombre}
                        secondary={`Cantidad: ${detalle.cantidad} | Precio: $${detalle.precioUnitario}`}
                      />
                      <ListItemSecondaryAction>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          ${(detalle.cantidad * detalle.precioUnitario).toFixed(2)}
                        </Typography>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < viewingItem.detalles.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>

      {/* Modal de confirmación para eliminar */}
      <Dialog
        open={confirmDeleteOpen}
        onClose={() => setConfirmDeleteOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ color: 'error.main', display: 'flex', alignItems: 'center' }}>
          <Delete sx={{ mr: 1 }} />
          Confirmar Eliminación
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Esta acción eliminará la venta y todos sus detalles
          </Alert>
          <Typography>
            ¿Estás seguro de que deseas eliminar esta venta?
          </Typography>
          {itemToDelete && (
            <Paper elevation={0} sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 1, mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Venta a eliminar:</strong>
              </Typography>
              <Typography variant="h6" color="error.main">
                {itemToDelete.cliente?.nombre} - ${itemToDelete.total?.toFixed(2)}
              </Typography>
              <Typography variant="body2">
                Fecha: {itemToDelete.fecha} | {itemToDelete.detalles?.length} productos
              </Typography>
            </Paper>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={() => setConfirmDeleteOpen(false)} 
            variant="outlined"
          >
            Cancelar
          </Button>
          <Button 
            onClick={confirmDelete} 
            variant="contained" 
            color="error"
            startIcon={<Delete />}
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VentasCrud;