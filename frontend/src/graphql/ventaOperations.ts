import { gql } from '@apollo/client';

export const GET_VENTAS = gql`
  query GetVentas {
    ventas {
      id
      fecha
      total
      cliente {
        id
        nombre
      }
      detalles {
        id
        cantidad
        precioUnitario
        subtotal
        producto {
          id
          nombre
        }
      }
    }
  }
`;

export const CREATE_VENTA = gql`
  mutation CreateVenta($input: VentaInput!) {
    createVenta(input: $input) {
      id
      fecha
      total
      cliente {
        id
        nombre
      }
      detalles {
        id
        cantidad
        precioUnitario
        subtotal
        producto {
          id
          nombre
        }
      }
    }
  }
`;

export const UPDATE_VENTA = gql`
  mutation UpdateVenta($id: ID!, $input: VentaInput!) {
    updateVenta(id: $id, input: $input) {
      id
      fecha
      total
      cliente {
        id
        nombre
      }
      detalles {
        id
        cantidad
        precioUnitario
        subtotal
        producto {
          id
          nombre
        }
      }
    }
  }
`;

export const DELETE_VENTA = gql`
  mutation DeleteVenta($id: ID!) {
    deleteVenta(id: $id)
  }
`;