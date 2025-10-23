import React from 'react';
import CrudTable from '../components/CrudTable';
import type { CrudConfig } from '../types';
import {
  GET_ALL_USUARIOS,
  CREATE_USUARIO,
  UPDATE_USUARIO,
  DELETE_USUARIO
} from '../graphql/operations';

const UsuariosPage: React.FC = () => {
  const config: CrudConfig = {
    title: 'Usuarios',
    fields: [
      { name: 'nombre', label: 'Nombre', type: 'text', required: true },
      { name: 'correo', label: 'Correo', type: 'text', required: true },
      { name: 'contrasena', label: 'Contraseña', type: 'password', required: true, hideInTable: true }
    ],
    queries: {
      getAll: GET_ALL_USUARIOS,
      create: CREATE_USUARIO,
      update: UPDATE_USUARIO,
      delete: DELETE_USUARIO
    }
  };

  return <CrudTable config={config} />;
};

export default UsuariosPage;