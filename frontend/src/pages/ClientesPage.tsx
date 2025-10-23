import React from 'react';
import CrudTable from '../components/CrudTable';
import type { CrudConfig } from '../types';
import {
  GET_ALL_CLIENTES,
  CREATE_CLIENTE,
  UPDATE_CLIENTE,
  DELETE_CLIENTE
} from '../graphql/operations';

const ClientesPage: React.FC = () => {
  const config: CrudConfig = {
    title: 'Clientes',
    fields: [
      { name: 'nombre', label: 'Nombre', type: 'text', required: true },
      { name: 'correo', label: 'Correo', type: 'text', required: true },
      { name: 'telefono', label: 'Teléfono', type: 'text' }
    ],
    queries: {
      getAll: GET_ALL_CLIENTES,
      create: CREATE_CLIENTE,
      update: UPDATE_CLIENTE,
      delete: DELETE_CLIENTE
    }
  };

  return <CrudTable config={config} />;
};

export default ClientesPage;