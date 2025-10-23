import { useQuery } from '@apollo/client/react';
import { 
  GET_ALL_CATEGORIAS, 
  GET_ALL_CLIENTES, 
  GET_ALL_USUARIOS, 
  GET_ALL_PRODUCTOS 
} from '../graphql/operations';

interface ReferenceItem {
  id: string;
  nombre?: string;
  email?: string;
  [key: string]: any;
}

interface UseReferenceDataReturn {
  categorias: ReferenceItem[];
  clientes: ReferenceItem[];
  usuarios: ReferenceItem[];
  productos: ReferenceItem[];
  loading: boolean;
  error: any;
}

interface UseReferenceDataOptions {
  loadCategorias?: boolean;
  loadClientes?: boolean;
  loadUsuarios?: boolean;
  loadProductos?: boolean;
}

export const useReferenceData = (options: UseReferenceDataOptions = {}): UseReferenceDataReturn => {
  const {
    loadCategorias = false,
    loadClientes = false,
    loadUsuarios = false,
    loadProductos = false
  } = options;

  const { 
    data: categoriasData, 
    loading: categoriasLoading, 
    error: categoriasError 
  } = useQuery(GET_ALL_CATEGORIAS, { skip: !loadCategorias });

  const { 
    data: clientesData, 
    loading: clientesLoading, 
    error: clientesError 
  } = useQuery(GET_ALL_CLIENTES, { skip: !loadClientes });

  const { 
    data: usuariosData, 
    loading: usuariosLoading, 
    error: usuariosError 
  } = useQuery(GET_ALL_USUARIOS, { skip: !loadUsuarios });

  const { 
    data: productosData, 
    loading: productosLoading, 
    error: productosError 
  } = useQuery(GET_ALL_PRODUCTOS, { skip: !loadProductos });

  const categorias = categoriasData?.categorias || [];
  const clientes = clientesData?.clientes || [];
  const usuarios = usuariosData?.usuarios || [];
  const productos = productosData?.productos || [];

  const loading = categoriasLoading || clientesLoading || usuariosLoading || productosLoading;
  const error = categoriasError || clientesError || usuariosError || productosError;

  return {
    categorias,
    clientes,
    usuarios,
    productos,
    loading,
    error
  };
};

// Utility function para convertir datos de referencia a options para selects
export const formatReferenceOptions = (data: ReferenceItem[], labelField: string = 'nombre') => {
  return data.map(item => ({
    value: item.id,
    label: item[labelField] || item.nombre || item.email || `Item ${item.id}`
  }));
};