/**
 * Configuración de base de datos para DL Service
 * Soporta PostgreSQL (Docker/Producción) con fallback a datos en memoria
 */

import { Pool } from 'pg';

const DATABASE_URL = process.env.DATABASE_URL || '';

let pool: Pool | null = null;

/**
 * Obtener conexión a la base de datos
 */
export function getDatabase(): Pool | null {
  if (!DATABASE_URL || !DATABASE_URL.startsWith('postgresql')) {
    console.warn('⚠️  DATABASE_URL no configurado o no es PostgreSQL. Usando cache en memoria.');
    return null;
  }

  if (!pool) {
    pool = new Pool({
      connectionString: DATABASE_URL,
      max: 10, // Máximo 10 conexiones
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    pool.on('error', (err) => {
      console.error('❌ Error inesperado en pool de PostgreSQL:', err);
    });

    console.log('✅ Pool de PostgreSQL inicializado');
  }

  return pool;
}

/**
 * Cerrar conexiones al finalizar
 */
export async function closeDatabase() {
  if (pool) {
    await pool.end();
    pool = null;
    console.log('🔒 Pool de PostgreSQL cerrado');
  }
}

/**
 * Verificar conexión a la base de datos
 */
export async function checkDatabaseHealth(): Promise<boolean> {
  const db = getDatabase();
  
  if (!db) {
    return false; // No hay DB configurada, usar cache en memoria
  }

  try {
    const result = await db.query('SELECT NOW()');
    return result.rows.length > 0;
  } catch (error) {
    console.error('❌ Health check de PostgreSQL falló:', error);
    return false;
  }
}

/**
 * Inicializar schema (ejecutar scripts de init.sql si es necesario)
 */
export async function initializeDatabase() {
  const db = getDatabase();
  
  if (!db) {
    console.log('ℹ️  Sin base de datos PostgreSQL. Datos se almacenarán en memoria.');
    return;
  }

  try {
    // Verificar que las tablas existen
    const result = await db.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
        AND table_name IN ('product_embeddings', 'copurchase_matrix', 'dl_models')
    `);

    if (result.rows.length === 3) {
      console.log('✅ Schema de PostgreSQL verificado OK');
    } else {
      console.warn('⚠️  Algunas tablas no existen. Asegúrate de ejecutar init.sql');
    }
  } catch (error) {
    console.error('❌ Error al verificar schema:', error);
  }
}

export default { getDatabase, closeDatabase, checkDatabaseHealth, initializeDatabase };
