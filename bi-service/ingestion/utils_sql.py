import pandas as pd
from typing import Dict, Any
from django.conf import settings
from sqlalchemy import create_engine, text


# =======================================================
# Normalizador universal de credenciales
# =======================================================
def _get_external_db():
    """
    Devuelve la config de la BD externa desde settings.EXTERNAL_DBS["EXTERNA"],
    o en su defecto usa settings.DATABASES["default"].
    """
    try:
        return settings.EXTERNAL_DBS["EXTERNA"]
    except Exception:
        return settings.DATABASES["default"]


def _norm(creds: dict | None) -> dict:
    """
    Normaliza credenciales para SQLAlchemy.
    """
    c = dict(creds or {})
    db = _get_external_db()

    c.setdefault("host", db.get("HOST", "postgres"))
    c.setdefault("port", db.get("PORT", 5432))
    c.setdefault("database", db.get("NAME"))
    c.setdefault("user", db.get("USER"))
    c.setdefault("password", db.get("PASSWORD", ""))
    c.setdefault("schema", db.get("SCHEMA", "public"))

    return c


def _get_engine(**db_credentials):
    """
    Retorna un SQLAlchemy engine listo para PostgreSQL.
    """
    c = _norm(db_credentials)
    uri = f"postgresql+psycopg2://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"
    return create_engine(uri, echo=False, future=True)


# =======================================================
# Obtener información de esquema
# =======================================================
def get_schema_info(schema: str, **db_credentials):
    """
    Retorna {tabla: {"columns": [...]}} para el esquema dado.
    """
    engine = _get_engine(**db_credentials)
    tablas: Dict[str, Dict[str, list]] = {}

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema AND table_type='BASE TABLE'
            ORDER BY table_name;
        """), {"schema": schema})

        for (table,) in result.fetchall():
            cols = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = :table
                ORDER BY ordinal_position;
            """), {"schema": schema, "table": table})
            columnas = [c[0] for c in cols.fetchall()]
            tablas[table] = {"columns": columnas}

    return tablas


# =======================================================
# Obtener claves foráneas
# =======================================================
def get_foreign_keys(schema: str, **db_credentials):
    """
    Devuelve lista de dicts con relaciones FK del esquema.
    """
    engine = _get_engine(**db_credentials)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                tc.table_name AS tabla_origen,
                kcu.column_name AS columna_fk,
                ccu.table_name AS tabla_destino,
                ccu.column_name AS columna_pk
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = :schema;
        """), {"schema": schema})

        rows = result.fetchall()

    return [
        {
            "tabla_origen": r[0],
            "columna_fk": r[1],
            "tabla_destino": r[2],
            "columna_pk": r[3],
        }
        for r in rows
    ]


# =======================================================
# Ejecutar SQL para gráficos Chart.js
# =======================================================
def ejecutar_sql_para_chart(sql: str, **db_credentials):
    """
    Ejecuta SQL y devuelve estructura básica para Chart.js.
    Usa SQLAlchemy para evitar advertencias de pandas.
    """
    engine = _get_engine(**db_credentials)

    # 🔹 Asegurar espacio en "JOIN" por si el LLM lo omite (pJOIN → p JOIN)
    sql = sql.replace('pJOIN', 'p JOIN').replace('vJOIN', 'v JOIN').replace('JOINJOIN', 'JOIN JOIN')

    df = None
    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql), conn)

    # Si no devolvió datos, intentar reescrituras simples y re-ejecutar como fallback.
    if df is None or df.shape[1] < 2 or df.empty:
        print(f"⚠️ Query returned empty or <2 columns. Attempting fallback rewrites...")
        # Obtener lista de tablas con conteo de filas para sugerir reemplazos
        tbl_counts = {}
        with engine.connect() as conn:
            try:
                res = conn.execute(text("""
                    SELECT table_name, (xpath('/row/count/text()', query_to_xml(format('SELECT COUNT(*) as count FROM %I', table_name), false, true, '')))[1]::text::int as cnt
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type='BASE TABLE';
                """))
                for row in res.fetchall():
                    tbl_counts[row[0]] = int(row[1] or 0)
                print(f"📊 Table counts: {tbl_counts}")
            except Exception as e:
                print(f"❌ Could not fetch table counts: {e}")
                tbl_counts = {}

        # intentos de reescritura: fecha_venta<->fecha, plural<->singular
        import re
        attempts = []
        
        # 1. Reemplazar fecha_venta por fecha
        attempts.append(sql.replace('fecha_venta', 'fecha'))
        
        # 2. Reemplazar tablas plurales por singular donde existan datos
        # Ej: ventas -> venta si venta tiene filas
        for plural in ['ventas', 'productos', 'clientes', 'categorias', 'usuarios', 'detalle_ventas']:
            singular = plural.rstrip('s')  # ventas->venta, detalle_ventas->detalle_venta
            if singular in tbl_counts and tbl_counts.get(singular, 0) > 0:
                # Reemplazo case-insensitive de FROM/JOIN tabla
                pattern = r'\b' + plural + r'\b'
                repl = singular
                attempt = re.sub(pattern, repl, sql, flags=re.IGNORECASE)
                attempts.append(attempt)
                # combinado con fecha_venta -> fecha
                attempts.append(re.sub(pattern, repl, sql.replace('fecha_venta', 'fecha'), flags=re.IGNORECASE))
        
        # 3. Combinar reemplazos múltiples si hay varias tablas plurales
        combined = sql.replace('fecha_venta', 'fecha')
        for plural in ['ventas', 'productos', 'clientes', 'categorias', 'usuarios']:
            singular = plural.rstrip('s')
            if singular in tbl_counts and tbl_counts.get(singular, 0) > 0:
                combined = re.sub(r'\b' + plural + r'\b', singular, combined, flags=re.IGNORECASE)
        attempts.append(combined)

        # Ejecutar intentos hasta que alguno devuelva datos (cada uno en nueva conexión)
        print(f"🔄 Trying {len(attempts)} fallback SQL variants...")
        for idx, alt_sql in enumerate(attempts):
            try:
                print(f"  Attempt {idx+1}: {alt_sql[:100]}")
                # Nueva conexión para evitar transaction aborted
                with engine.connect() as conn_alt:
                    df_alt = pd.read_sql_query(text(alt_sql), conn_alt)
                print(f"    → Result: shape={df_alt.shape}, empty={df_alt.empty}")
                if df_alt.shape[1] >= 2 and not df_alt.empty:
                    df = df_alt
                    sql = alt_sql
                    print(f"✅ Fallback SQL exitoso: {alt_sql}")
                    break
            except Exception as e:
                print(f"    → Error: {e}")
                continue

    if df is None or df.shape[1] < 2 or df.empty:
        return {"labels": [], "datasets": [{"data": []}]}

    labels = df.iloc[:, 0].astype(str).tolist()

    try:
        values = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0).tolist()
    except Exception:
        values = df.iloc[:, 1].tolist()

    return {"labels": labels, "datasets": [{"data": values}]}


# =======================================================
# Reducir esquema para LLM
# =======================================================
def reduce_schema(schema_dict: Dict[str, Any]) -> Dict[str, list]:
    """
    Devuelve {"tabla": ["col1", "col2", ...]} desde estructuras complejas.
    """
    reduced: Dict[str, list] = {}
    for table, info in (schema_dict or {}).items():
        if isinstance(info, dict) and "columns" in info:
            reduced[table] = list(info["columns"])
        elif isinstance(info, list):
            reduced[table] = list(info)
        else:
            reduced[table] = []
    return reduced
