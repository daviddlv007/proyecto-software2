import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useReferenceData } from '../hooks/useReferenceData';

const DebugInfo: React.FC = () => {
  const { categorias, clientes, loading, error } = useReferenceData();

  if (loading) return <div>Cargando datos de referencia...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Paper sx={{ p: 2, m: 2 }}>
      <Typography variant="h6">Debug - Datos de Referencia</Typography>
      
      <Box mt={2}>
        <Typography variant="subtitle1">Categorías ({categorias.length}):</Typography>
        <pre>{JSON.stringify(categorias, null, 2)}</pre>
      </Box>
      
      <Box mt={2}>
        <Typography variant="subtitle1">Clientes ({clientes.length}):</Typography>
        <pre>{JSON.stringify(clientes, null, 2)}</pre>
      </Box>
    </Paper>
  );
};

export default DebugInfo;