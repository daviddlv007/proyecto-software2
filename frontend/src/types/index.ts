export interface Categoria {
  id: string;
  nombre: string;
  descripcion?: string;
}

export interface Producto {
  id: string;
  nombre: string;
  descripcion?: string;
  imagenUrl?: string;
  precio: number;
  stock?: number;
  categoria: Categoria;
}

export interface Cliente {
  id: string;
  nombre: string;
  correo: string;
  telefono?: string;
}

export interface Usuario {
  id: string;
  nombre: string;
  correo: string;
  contrasena: string;
}

export interface Venta {
  id: string;
  cliente: Cliente;
  fecha: string;
  total: number;
}

export interface DetalleVenta {
  id: string;
  venta: Venta;
  producto: Producto;
  cantidad: number;
  precioUnitario: number;
}

export interface FieldConfig {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'password' | 'display';
  required?: boolean;
  options?: { value: string; label: string }[];
  hideInTable?: boolean; // Ocultar campo en la tabla (útil para contraseñas, URLs largas, etc.)
}

export interface CrudConfig {
  title: string;
  fields: FieldConfig[];
  queries: {
    getAll: any;
    create: any;
    update: any;
    delete: any;
  };
  foreignKeys?: { [key: string]: any[] };
  hasDetails?: boolean;
  detailsConfig?: CrudConfig;
}

export interface FormData {
  [key: string]: any;
}