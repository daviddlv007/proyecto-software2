import React from 'react';
import VentasCrud from '../components/VentasCrud';
import type { CrudConfig } from '../types';
import {
  GET_ALL_VENTAS,
  CREATE_VENTA,
  UPDATE_VENTA,
  DELETE_VENTA
} from '../graphql/operations';

const VentasPage: React.FC = () => {
  const config: CrudConfig = {
    title: 'Ventas',
    fields: [
      { name: 'clienteId', label: 'Cliente', type: 'select' },
      { name: 'fecha', label: 'Fecha', type: 'text' },
      { name: 'total', label: 'Total', type: 'number' }
    ],
    queries: {
      getAll: GET_ALL_VENTAS,
      create: CREATE_VENTA,
      update: UPDATE_VENTA,
      delete: DELETE_VENTA
    },
    hasDetails: true
  };

  return <VentasCrud config={config} />;
};

export default VentasPage;