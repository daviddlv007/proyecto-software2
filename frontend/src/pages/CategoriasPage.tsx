import React from 'react';
import CrudTable from '../components/CrudTable';
import type { CrudConfig } from '../types';
import {
  GET_ALL_CATEGORIAS,
  CREATE_CATEGORIA,
  UPDATE_CATEGORIA,
  DELETE_CATEGORIA
} from '../graphql/operations';

const CategoriasPage: React.FC = () => {
  const config: CrudConfig = {
    title: 'Categorías',
    fields: [
      { name: 'nombre', label: 'Nombre', type: 'text', required: true },
      { name: 'descripcion', label: 'Descripción', type: 'text' }
    ],
    queries: {
      getAll: GET_ALL_CATEGORIAS,
      create: CREATE_CATEGORIA,
      update: UPDATE_CATEGORIA,
      delete: DELETE_CATEGORIA
    }
  };

  return <CrudTable config={config} />;
};

export default CategoriasPage;