import { gql } from '@apollo/client';

export const GET_CLIENTES = gql`
  query GetClientes {
    clientes {
      id
      nombre
      correo
      telefono
    }
  }
`;

export const CREATE_CLIENTE = gql`
  mutation CreateCliente($input: ClienteInput!) {
    createCliente(input: $input) {
      id
      nombre
      correo
      telefono
    }
  }
`;

export const UPDATE_CLIENTE = gql`
  mutation UpdateCliente($id: ID!, $input: ClienteInput!) {
    updateCliente(id: $id, input: $input) {
      id
      nombre
      correo
      telefono
    }
  }
`;

export const DELETE_CLIENTE = gql`
  mutation DeleteCliente($id: ID!) {
    deleteCliente(id: $id)
  }
`;