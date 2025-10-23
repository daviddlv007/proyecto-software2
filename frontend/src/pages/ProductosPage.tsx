import React from 'react';
import { CircularProgress, Box } from '@mui/material';
import CrudTable from '../components/CrudTable';
import type { CrudConfig } from '../types';
import {
  GET_ALL_PRODUCTOS,
  CREATE_PRODUCTO,
  UPDATE_PRODUCTO,
  DELETE_PRODUCTO
} from '../graphql/operations';
import { useReferenceData, formatReferenceOptions } from '../hooks/useReferenceData';

const ProductosPage: React.FC = () => {
  const { categorias, loading, error } = useReferenceData({ loadCategorias: true });

  // Mostrar loading mientras se cargan las referencias
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  // Mostrar error si falla la carga de referencias
  if (error) {
    return (
      <Box p={2}>
        <div>Error cargando datos de referencia: {error.message}</div>
      </Box>
    );
  }

  const config: CrudConfig = {
    title: 'Productos',
    fields: [
      { name: 'nombre', label: 'Nombre', type: 'text', required: true },
      { name: 'descripcion', label: 'Descripción', type: 'text' },
      { name: 'imagenUrl', label: 'URL Imagen', type: 'text', hideInTable: true },
      { name: 'precio', label: 'Precio', type: 'number', required: true },
      { name: 'stock', label: 'Stock', type: 'number' },
      { 
        name: 'categoriaId', 
        label: 'Categoría', 
        type: 'select', 
        required: true,
        options: formatReferenceOptions(categorias, 'nombre')
      },
      // Campo solo para mostrar en la tabla
      { name: 'categoria.nombre', label: 'Categoría', type: 'display' }
    ],
    queries: {
      getAll: GET_ALL_PRODUCTOS,
      create: CREATE_PRODUCTO,
      update: UPDATE_PRODUCTO,
      delete: DELETE_PRODUCTO
    },
    foreignKeys: {
      categoriaId: categorias
    }
  };

  return <CrudTable config={config} />;
};

export default ProductosPage;