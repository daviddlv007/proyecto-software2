import { gql } from '@apollo/client';

export const GET_PRODUCTOS = gql`
  query GetProductos {
    productos {
      id
      nombre
      descripcion
      imagenUrl
      precio
      stock
      categoria {
        id
        nombre
      }
    }
  }
`;

export const CREATE_PRODUCTO = gql`
  mutation CreateProducto($input: ProductoInput!) {
    createProducto(input: $input) {
      id
      nombre
      descripcion
      imagenUrl
      precio
      stock
      categoria {
        id
        nombre
      }
    }
  }
`;

export const UPDATE_PRODUCTO = gql`
  mutation UpdateProducto($id: ID!, $input: ProductoInput!) {
    updateProducto(id: $id, input: $input) {
      id
      nombre
      descripcion
      imagenUrl
      precio
      stock
      categoria {
        id
        nombre
      }
    }
  }
`;

export const DELETE_PRODUCTO = gql`
  mutation DeleteProducto($id: ID!) {
    deleteProducto(id: $id)
  }
`;