import React, { useState } from 'react';
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
  MenuItem
} from '@mui/material';
import { Edit, Delete, Add } from '@mui/icons-material';
import { useQuery, useMutation } from '@apollo/client/react';
import type { CrudConfig, FormData, FieldConfig } from '../types';

interface CrudTableProps {
  config: CrudConfig;
}

const CrudTable: React.FC<CrudTableProps> = ({ config }) => {
  const [open, setOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<any>(null);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState<FormData>({});
  const [error, setError] = useState('');
  const [data, setData] = useState<any[]>([]);

  // GraphQL hooks - AHORA FUNCIONA CON REACT 19!
  const { data: queryData, refetch } = useQuery(config.queries.getAll, {
    skip: !config.queries?.getAll, // Skip if no query provided
  });

  const [createMutation] = useMutation(config.queries.create, {
    onCompleted: () => {
      setOpen(false);
      setFormData({});
      setEditingItem(null);
      if (refetch) refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  const [updateMutation] = useMutation(config.queries.update, {
    onCompleted: () => {
      setOpen(false);
      setFormData({});
      setEditingItem(null);
      if (refetch) refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  const [deleteMutation] = useMutation(config.queries.delete, {
    onCompleted: () => {
      if (refetch) refetch();
    },
    onError: (error: any) => setError(error.message)
  });

  // Extract data from GraphQL response or use local data
  const displayData = queryData ? (queryData as any)[Object.keys(queryData)[0]] || [] : data;

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({});
    setOpen(true);
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    const initialData: FormData = {};
    config.fields.forEach(field => {
      if (field.name.includes('.')) {
        const [parent, child] = field.name.split('.');
        initialData[field.name] = item[parent]?.[child] || '';
      } else {
        initialData[field.name] = item[field.name] || '';
      }
    });
    setFormData(initialData);
    setOpen(true);
  };

  const handleDelete = (item: any) => {
    setItemToDelete(item);
    setConfirmDeleteOpen(true);
  };

  const confirmDelete = async () => {
    if (itemToDelete) {
      try {
        if (config.queries?.delete && deleteMutation) {
          // Use GraphQL
          await deleteMutation({ variables: { id: itemToDelete.id } });
        } else {
          // Use local data
          setData(prev => prev.filter(item => item.id !== itemToDelete.id));
        }
        setConfirmDeleteOpen(false);
        setItemToDelete(null);
      } catch (err) {
        console.error('Error deleting:', err);
        setError('Error al eliminar el elemento');
      }
    }
  };

  const cancelDelete = () => {
    setConfirmDeleteOpen(false);
    setItemToDelete(null);
  };

  const handleSave = async () => {
    setError('');
    
    // Validar campos requeridos
    const requiredFields = config.fields.filter(field => field.required && field.type !== 'display');
    const missingFields = requiredFields.filter(field => !formData[field.name] || formData[field.name] === '');
    
    if (missingFields.length > 0) {
      setError(`Campos requeridos: ${missingFields.map(f => f.label).join(', ')}`);
      return;
    }
    
    // Procesar datos del formulario y convertir tipos
    const processedData = { ...formData };
    
    // Convertir campos numéricos (precio, stock, etc.)
    config.fields.forEach(field => {
      if (field.type === 'number' && processedData[field.name]) {
        const rawValue = processedData[field.name];
        // Limpiar espacios y convertir a número
        const cleanValue = typeof rawValue === 'string' ? rawValue.trim() : rawValue;
        const numericValue = parseFloat(cleanValue);
        
        // Solo asignar si es un número válido
        if (!isNaN(numericValue)) {
          processedData[field.name] = numericValue;
        } else {
          // Si no es un número válido y es requerido, mostrar error
          if (field.required) {
            setError(`${field.label} debe ser un número válido`);
            return;
          }
          // Si no es requerido, eliminar el campo
          delete processedData[field.name];
        }
      }
    });
    
    // Manejar claves foráneas - agregar objeto de referencia
    if (config.foreignKeys) {
      Object.keys(config.foreignKeys).forEach(foreignKey => {
        if (processedData[foreignKey]) {
          const referencedItem = config.foreignKeys![foreignKey].find(
            item => item.id === processedData[foreignKey]
          );
          if (referencedItem) {
            if (config.queries) {
              // Para GraphQL, solo necesitamos el ID de la referencia
              // El resolver se encargará de cargar la entidad completa
            } else {
              // Para datos locales, agregar el objeto referenciado
              const entityName = foreignKey.replace('Id', '');
              processedData[entityName] = referencedItem;
            }
          }
        }
      });
    }

    try {
      if (config.queries && createMutation && updateMutation) {
        // Log para debugging
        console.log('Datos procesados para GraphQL:', processedData);
        // Validar campos requeridos
        if (config.fields) {
          for (const field of config.fields) {
            // Si el campo requerido no está presente, usar string vacío
            if (field.required && (processedData[field.name] === undefined || processedData[field.name] === null)) {
              processedData[field.name] = '';
            }
            if (field.required && processedData[field.name].toString().trim() === '') {
              setError(`El campo '${field.label}' es obligatorio.`);
              return;
            }
          }
        }
        // Use GraphQL with Input types
        if (editingItem) {
          await updateMutation({ 
            variables: { 
              id: editingItem.id, 
              input: processedData 
            } 
          });
        } else {
          await createMutation({ variables: { input: processedData } });
        }
      } else {
        // Use local data
        if (editingItem) {
          setData(prev => prev.map(item => 
            item.id === editingItem.id 
              ? { ...item, ...processedData, id: editingItem.id }
              : item
          ));
        } else {
          const newItem = { ...processedData, id: Date.now().toString() };
          setData(prev => [...prev, newItem]);
        }
        setOpen(false);
        setFormData({});
        setEditingItem(null);
      }
    } catch (err) {
      console.error('Error saving:', err);
      setError('Error al guardar el elemento');
    }
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }));
  };

  const renderField = (field: FieldConfig) => {
    const value = formData[field.name] || '';

    // No renderizar campos de solo visualización en formularios
    if (field.type === 'display') {
      return null;
    }

    if (field.type === 'select' && field.options) {
      return (
        <FormControl fullWidth margin="normal" key={field.name}>
          <InputLabel>{field.label}</InputLabel>
          <Select
            value={value}
            label={field.label}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
          >
            {field.options.map(option => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      );
    }

    return (
      <TextField
        key={field.name}
        margin="normal"
        fullWidth
        label={field.label}
        type={field.type === 'password' ? 'password' : field.type === 'number' ? 'number' : 'text'}
        value={value}
        onChange={(e) => handleFieldChange(field.name, e.target.value)}
        required={field.required}
      />
    );
  };

  const getNestedValue = (obj: any, path: string) => {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">{config.title}</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreate}
        >
          Crear Nuevo
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {config.fields
                .filter(field => !field.hideInTable && (field.type !== 'select' || field.name.includes('.')))
                .map(field => (
                <TableCell key={field.name}>{field.label}</TableCell>
              ))}
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {displayData.map((item: any) => (
              <TableRow key={item.id}>
                {config.fields
                  .filter(field => !field.hideInTable && (field.type !== 'select' || field.name.includes('.')))
                  .map(field => (
                  <TableCell key={field.name}>
                    {field.type === 'number' && !field.name.includes('.') ? 
                      (typeof getNestedValue(item, field.name) === 'number' ? 
                        `$${getNestedValue(item, field.name).toFixed(2)}` : 
                        getNestedValue(item, field.name)
                      ) :
                      getNestedValue(item, field.name)
                    }
                  </TableCell>
                ))}
                <TableCell>
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

      {/* Dialog para crear/editar */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? `Editar ${config.title}` : `Crear ${config.title}`}
        </DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {config.fields.map(renderField)}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancelar</Button>
          <Button onClick={handleSave} variant="contained">
            {editingItem ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Modal de confirmación para eliminar */}
      <Dialog
        open={confirmDeleteOpen}
        onClose={cancelDelete}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
          }
        }}
      >
        <DialogTitle sx={{ 
          pb: 1, 
          display: 'flex', 
          alignItems: 'center',
          color: 'error.main'
        }}>
          <Delete sx={{ mr: 1 }} />
          Confirmar Eliminación
        </DialogTitle>
        <DialogContent sx={{ py: 2 }}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Esta acción no se puede deshacer
          </Alert>
          <Typography variant="body1" sx={{ mb: 2 }}>
            ¿Estás seguro de que deseas eliminar este elemento?
          </Typography>
          {itemToDelete && (
            <Paper elevation={0} sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                <strong>Elemento a eliminar:</strong>
              </Typography>
              <Typography variant="h6" color="error.main">
                {itemToDelete.nombre || itemToDelete.correo || itemToDelete.id || 'Sin identificador'}
              </Typography>
              {itemToDelete.descripcion && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {itemToDelete.descripcion}
                </Typography>
              )}
            </Paper>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button 
            onClick={cancelDelete} 
            variant="outlined" 
            size="large"
            sx={{ minWidth: 100 }}
          >
            Cancelar
          </Button>
          <Button 
            onClick={confirmDelete} 
            variant="contained" 
            color="error"
            size="large"
            startIcon={<Delete />}
            sx={{ minWidth: 100 }}
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CrudTable;