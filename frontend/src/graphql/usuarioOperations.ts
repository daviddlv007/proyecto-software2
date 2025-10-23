import { gql } from '@apollo/client';

export const GET_USUARIOS = gql`
  query GetUsuarios {
    usuarios {
      id
      nombre
      correo
      contrasena
    }
  }
`;

export const CREATE_USUARIO = gql`
  mutation CreateUsuario($input: UsuarioInput!) {
    createUsuario(input: $input) {
      id
      nombre
      correo
      contrasena
    }
  }
`;

export const UPDATE_USUARIO = gql`
  mutation UpdateUsuario($id: ID!, $input: UsuarioInput!) {
    updateUsuario(id: $id, input: $input) {
      id
      nombre
      correo
      contrasena
    }
  }
`;

export const DELETE_USUARIO = gql`
  mutation DeleteUsuario($id: ID!) {
    deleteUsuario(id: $id)
  }
`;