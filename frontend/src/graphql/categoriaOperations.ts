import { gql } from '@apollo/client';

export const GET_CATEGORIAS = gql`
  query GetCategorias {
    categorias {
      id
      nombre
      descripcion
    }
  }
`;

export const CREATE_CATEGORIA = gql`
  mutation CreateCategoria($input: CategoriaInput!) {
    createCategoria(input: $input) {
      id
      nombre
      descripcion
    }
  }
`;

export const UPDATE_CATEGORIA = gql`
  mutation UpdateCategoria($id: ID!, $input: CategoriaInput!) {
    updateCategoria(id: $id, input: $input) {
      id
      nombre
      descripcion
    }
  }
`;

export const DELETE_CATEGORIA = gql`
  mutation DeleteCategoria($id: ID!) {
    deleteCategoria(id: $id)
  }
`;