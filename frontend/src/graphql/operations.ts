import { gql } from '@apollo/client';

// CATEGORIAS
export const GET_ALL_CATEGORIAS = gql`
  query GetAllCategorias {
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

// PRODUCTOS
export const GET_ALL_PRODUCTOS = gql`
  query GetAllProductos {
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

// CLIENTES
export const GET_ALL_CLIENTES = gql`
  query GetAllClientes {
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

// USUARIOS
export const GET_ALL_USUARIOS = gql`
  query GetAllUsuarios {
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

// VENTAS
export const GET_ALL_VENTAS = gql`
  query GetAllVentas {
    ventas {
      id
      cliente {
        id
        nombre
      }
      fecha
      total
      detalles {
        id
        producto {
          id
          nombre
        }
        cantidad
        precioUnitario
        subtotal
      }
    }
  }
`;

export const CREATE_VENTA = gql`
  mutation CreateVenta($input: VentaInput!) {
    createVenta(input: $input) {
      id
      cliente {
        id
        nombre
      }
      fecha
      total
      detalles {
        id
        producto {
          id
          nombre
        }
        cantidad
        precioUnitario
        subtotal
      }
    }
  }
`;

export const UPDATE_VENTA = gql`
  mutation UpdateVenta($id: ID!, $input: VentaInput!) {
    updateVenta(id: $id, input: $input) {
      id
      cliente {
        id
        nombre
      }
      fecha
      total
      detalles {
        id
        producto {
          id
          nombre
        }
        cantidad
        precioUnitario
        subtotal
      }
    }
  }
`;

export const DELETE_VENTA = gql`
  mutation DeleteVenta($id: ID!) {
    deleteVenta(id: $id)
  }
`;