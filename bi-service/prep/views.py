# ingestion/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import text, inspect
import pandas as pd
import json
from datetime import datetime, date, time
import re
import os
from django.conf import settings
import google.generativeai as genai

from ingestion.models import DataSource
from ingestion.services import get_engine
from config.db_config import get_core_raw_connection  

from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID

def _to_jsonable(v):
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (UUID, )):
        return str(v)
    # opcional: memoryview → str/bytes
    if isinstance(v, memoryview):
        try:
            return v.tobytes().decode("utf-8", "ignore")
        except Exception:
            return v.tobytes()
    return v

def _jsonify(obj):
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(x) for x in obj]
    return _to_jsonable(obj)

# alias para menos tecleo si prefieres
_jsonable = _jsonify

def get_column_types(conn, schema, table):
    """
    Devuelve {col_en_minusculas: data_type}
    Ej: 'time without time zone', 'timestamp without time zone', 'integer', etc.
    """
    rows = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
    """), {"schema": schema, "table": table}).fetchall()
    return {r[0].lower(): r[1] for r in rows}

def coerce_value_for_type(data_type: str | None, value):
    """
    Convierte strings del front a tipos Python que psycopg2 sabe adaptar.
    - time: acepta 'H', 'HH', 'HH:MM', 'HH:MM:SS' → datetime.time
    - timestamp: ISO 'YYYY-MM-DD HH:MM:SS' o 'YYYY-MM-DDTHH:MM:SS' → datetime
    - date: 'YYYY-MM-DD' → date
    - int/float/bool: castea básico
    Otros tipos: devuelve el valor tal cual.
    """
    if value is None or value == "":
        return None
    if not data_type:
        return value

    dt = data_type.lower()

    # timestamp
    if dt.startswith("timestamp"):
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace(" ", "T"))

    # date
    if dt == "date":
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        return date.fromisoformat(str(value))

    # time
    if dt.startswith("time"):
        if isinstance(value, time):
            return value
        s = str(value).strip()

        # 'H' o 'HH'
        if re.fullmatch(r"\d{1,2}", s):
            h = int(s)
            if h == 24:  # normaliza 24:00 → 00:00:00
                h = 0
            return time(hour=h, minute=0, second=0)

        # 'HH:MM'
        m = re.fullmatch(r"(\d{1,2}):(\d{1,2})", s)
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            if h == 24 and mi == 0:
                h = 0
            return time(hour=h, minute=mi, second=0)

        # 'HH:MM:SS'
        m = re.fullmatch(r"(\d{1,2}):(\d{1,2}):(\d{1,2})", s)
        if m:
            h, mi, se = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if h == 24 and mi == 0 and se == 0:
                h = 0
            return time(hour=h, minute=mi, second=se)

        # último intento
        try:
            return time.fromisoformat(s)
        except Exception:
            raise ValueError(f"Formato de hora inválido: {s} (usa HH, HH:MM o HH:MM:SS)")

    # integer
    if dt in ("integer", "smallint", "bigint"):
        return int(value)

    # float / numeric
    if dt in ("numeric", "real", "double precision", "decimal"):
        return float(value)

    # boolean
    if dt == "boolean":
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in ("true", "t", "1", "yes", "y", "si", "sí"):
            return True
        if s in ("false", "f", "0", "no", "n"):
            return False
        # deja que la DB se queje si no matchea
        return value

    # por defecto, deja el string
    return value

def coerce_value_auto(colname: str, types_map_lc: dict, value):
    """
    Usa el tipo de la columna (case-insensitive) y, si no hay tipo,
    intenta inferir TIME por la forma del string ('00', '7', '07:30', etc.).
    """
    from datetime import time
    import re

    dtype = types_map_lc.get(colname.lower())
    try:
        return coerce_value_for_type(dtype, value)
    except Exception:
        # Fallback solo para hora con strings cortos
        if value is None or value == "":
            return None
        s = str(value).strip()
        if re.fullmatch(r"\d{1,2}", s):
            h = int(s)
            if h == 24: h = 0
            return time(hour=h, minute=0, second=0)
        m = re.fullmatch(r"(\d{1,2}):(\d{1,2})", s)
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            if h == 24 and mi == 0: h = 0
            return time(hour=h, minute=mi, second=0)
        return value


def qi(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'

def list_columns(conn, schema, table):
    return [c["name"] for c in inspect(conn).get_columns(table, schema=schema)]

def pk_columns(conn, schema, table):
    # Primero intenta con SQLAlchemy
    try:
        pk = inspect(conn).get_pk_constraint(table, schema=schema).get("constrained_columns") or []
        if pk:
            return pk
    except Exception:
        pass
    # Fallback Postgres
    res = conn.execute(text("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_class t ON t.oid = i.indrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(i.indkey)
        WHERE i.indisprimary
          AND n.nspname = :schema
          AND t.relname = :table
        ORDER BY a.attnum
    """), {"schema": schema, "table": table}).fetchall()
    return [r[0] for r in res]


def prep_schema_index_view(request):
    # 1) Saca los schemas del usuario (vía DataSource)
    sources = DataSource.objects.filter(owner=request.user).order_by("-created_at")
    schema_to_file = {s.internal_schema: s.name for s in sources if s.internal_schema}

    if not schema_to_file:
        return render(request, "prep/prep_schema_index.html", {"items": []})

    schemas = list(schema_to_file.keys())

    # 2) Métricas rápidas por schema:
    # - Conteo de tablas
    # - Filas aproximadas (reltuples)
    # - Tamaño total (sum rela+idx)
    items = []
    core_conn = get_core_raw_connection()
    with core_conn.cursor() as cur:
        # tablas por schema
        cur.execute("""
            SELECT table_schema, COUNT(*) AS table_count
            FROM information_schema.tables
            WHERE table_type='BASE TABLE' AND table_schema = ANY(%s)
            GROUP BY table_schema
        """, [schemas])
        table_counts = {r[0]: r[1] for r in cur.fetchall()}

        # filas aprox y tamaño por schema (sumando por tabla)
        cur.execute("""
            SELECT n.nspname AS schema,
                   SUM(COALESCE(c.reltuples,0))::bigint AS approx_rows,
                   SUM(pg_total_relation_size(c.oid)) AS total_size
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = ANY(%s)
              AND c.relkind='r'
            GROUP BY n.nspname
        """, [schemas])
        stats = {r[0]: {"approx_rows": r[1], "total_size": r[2]} for r in cur.fetchall()}

    # 3) Armar filas
    for s in schemas:
        items.append({
            "schema": s,
            "file": schema_to_file.get(s, s),
            "table_count": table_counts.get(s, 0),
            "approx_rows": stats.get(s, {}).get("approx_rows", 0),
            "total_size": stats.get(s, {}).get("total_size", 0),
        })

    # Orden opcional por fecha de subida (ya viene de DataSource)
    ordered = sorted(items, key=lambda x: list(schema_to_file.keys()).index(x["schema"]))
    return render(request, "prep/prep_schema_index.html", {"items": ordered})

# ---------- Helpers ----------
def list_user_schemas(user):
    """Devuelve [{'file':<nombre>, 'schema':<schema>}] de los DataSource del usuario."""
    sources = DataSource.objects.filter(owner=user).order_by("-created_at")
    items = []
    for src in sources:
        if src.internal_schema:
            items.append({"file": src.name, "schema": src.internal_schema})
    return items

def list_tables_in_schema(schema: str):
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema AND table_type='BASE TABLE'
            ORDER BY table_name
        """), {"schema": schema})
        return [r[0] for r in res]

def fetch_page(schema: str, table: str, page: int, page_size: int):
    """Lee una página de datos con COUNT(*) para el total."""
    engine = get_engine()
    offset = (page - 1) * page_size

    # (Opcional pero recomendable) validar schema/table si vienen de usuario.
    safe_schema = schema.replace('"', '')
    safe_table  = table.replace('"', '')

    with engine.begin() as conn:
        total = conn.execute(
            text(f'SELECT COUNT(*) FROM "{safe_schema}"."{safe_table}"')
        ).scalar_one()  # o .scalar() si tu DB puede devolver None

        # ❗ NO hagas .fetchall() antes de leer las keys; primero conserva el Result
        result = conn.execute(
            text(f'SELECT * FROM "{safe_schema}"."{safe_table}" LIMIT :limit OFFSET :offset'),
            {"limit": page_size, "offset": offset},
        )

        # ✅ nombres reales de columnas del SELECT (sirve aunque no haya filas)
        cols = list(result.keys())

        # ✅ cada fila a dict de forma estable
        data = [dict(row._mapping) for row in result]  # iterar el Result consume sus filas

    return total, cols, data

def quoted_ident(s):  # por seguridad
    return '"' + s.replace('"', '""') + '"'

# ---------- 1) Vista: Picker schemas/tablas ----------
@login_required
def prep_table_picker_view(request, schema=None):
    """Lista schemas (del usuario) y, al seleccionar, muestra tablas. Luego ‘Ir al editor’."""
    selected_schema = schema
    tables = list_tables_in_schema(selected_schema) if selected_schema else []
    ctx = {
        "selected_schema": selected_schema,
        "tables": tables,
    }
    return render(request, "prep/prep_picker.html", ctx)

# ---------- 2) Vista: Editor (página) ----------
@login_required
def prep_editor_view(request, schema, table):
    """Renderiza el editor (grid + botones), el grid se alimenta por AJAX /data/."""
    return render(request, "prep/prep_editor.html", {
        "schema": schema,
        "table": table
    })

# ---------- APIs JSON ----------
@login_required
@require_http_methods(["GET"])
def get_table_data(request, schema, table):
    page = int(request.GET.get("page", "1"))
    page_size = int(request.GET.get("page_size", "50"))
    engine = get_engine()
    offset = (page - 1) * page_size

    with engine.begin() as conn:
        total = conn.execute(text(f'SELECT COUNT(*) FROM {qi(schema)}.{qi(table)}')).scalar_one()
        pks = pk_columns(conn, schema, table)

        # Si no hay PK, incluimos ctid (Postgres) como pseudo PK oculto
        ctid_sel = ', ctid::text AS "_ctid"' if not pks else ''

        result = conn.execute(
            text(f'SELECT *{ctid_sel} FROM {qi(schema)}.{qi(table)} LIMIT :lim OFFSET :off'),
            {"lim": page_size, "off": offset}
        )
        cols = list(result.keys())
        rows = [dict(r._mapping) for r in result]

    return JsonResponse({"total": total, "columns": cols, "rows": rows, "pk": pks})

@login_required
@require_http_methods(["POST"])
def update_rows(request, schema, table):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        updates = payload.get("updates") or []
        if not updates:
            return JsonResponse({"ok": False, "error": "updates vacío"}, status=400)

        engine = get_engine()
        updated, inserted = 0, 0

        with engine.begin() as conn:
            pks = pk_columns(conn, schema, table)
            cols = set(c.lower() for c in list_columns(conn, schema, table))
            types_map = get_column_types(conn, schema, table)

            for up in updates:
                pkvals = up.get("pk") or {}
                changes = up.get("changes") or {}
                if not changes:
                    continue

                # Si hay PKs definidos, exigimos todas las PKs para UPDATE
                if pks:
                    missing = [col for col in pks if col not in pkvals]
                    if missing:
                        # Si faltan PKs, interpretamos que es una fila nueva → INSERT
                        cols_used = [c for c in changes.keys() if c.lower() in cols]
                        if not cols_used:
                            continue
                        collist = ", ".join(qi(c) for c in cols_used)
                        params = {f"v{i}": changes[c] for i, c in enumerate(cols_used)}
                        values = ", ".join(f":v{i}" for i in range(len(cols_used)))
                        q = (
                            f'INSERT INTO {qi(schema)}.{qi(table)} ({collist}) '
                            f'VALUES ({values}) RETURNING *'
                        )
                        res = conn.execute(text(q), params)
                        _ = res.mappings().first()  # si quieres podrías acumular filas
                        inserted += 1
                        continue

                    # UPDATE normal con PK
                    set_parts, params = [], {}
                    for i, (col, val) in enumerate(changes.items()):
                        if col.lower() not in cols:
                            return JsonResponse({"ok": False, "error": f"Columna no existe: {col}"}, status=400)
                        try:
                            coerced = coerce_value_auto(col, types_map_lc, val)
                        except Exception as e:
                            return JsonResponse(
                                {"ok": False, "error": f"Valor inválido para '{col}' ({types_map_lc.get(col.lower())}): {e}"},
                                status=400
                            )
                        set_parts.append(f"{qi(col)} = :v{i}")
                        params[f"v{i}"] = coerced

                    where_parts = []
                    for j, col in enumerate(pks):
                        where_parts.append(f"{qi(col)} = :k{j}")
                        params[f"k{j}"] = pkvals[col]
                    q = (
                        f'UPDATE {qi(schema)}.{qi(table)} SET ' + ", ".join(set_parts) +
                        " WHERE " + " AND ".join(where_parts)
                    )
                    conn.execute(text(q), params)
                    updated += 1
                    continue

                # Sin PK: si llega _ctid → UPDATE; si no → INSERT
                if "_ctid" in pkvals and pkvals["_ctid"]:
                    # UPDATE por ctid
                    set_parts, params = [], {}
                    for i, (col, val) in enumerate(changes.items()):
                        if col.lower() not in cols:
                            return JsonResponse({"ok": False, "error": f"Columna no existe: {col}"}, status=400)
                        set_parts.append(f"{qi(col)} = :v{i}")
                        params[f"v{i}"] = val
                    params["k0"] = pkvals["_ctid"]
                    q = (
                        f'UPDATE {qi(schema)}.{qi(table)} SET ' + ", ".join(set_parts) +
                        " WHERE ctid = :k0"
                    )
                    conn.execute(text(q), params)
                    updated += 1
                else:
                    # INSERT (fallback) y devolvemos el _ctid generado
                    cols_used = [c for c in changes.keys() if c.lower() in cols]
                    if not cols_used:
                        continue
                    collist = ", ".join(qi(c) for c in cols_used)
                    params = {f"v{i}": changes[c] for i, c in enumerate(cols_used)}
                    values = ", ".join(f":v{i}" for i in range(len(cols_used)))
                    q = (
                        f'INSERT INTO {qi(schema)}.{qi(table)} ({collist}) '
                        f'VALUES ({values}) RETURNING *, ctid::text AS "_ctid"'
                    )
                    res = conn.execute(text(q), params)
                    _ = res.mappings().first()
                    inserted += 1

        return JsonResponse({"ok": True, "updated": updated, "inserted": inserted})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def insert_rows(request, schema, table):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        rows = payload.get("rows") or []
        if not rows:
            return JsonResponse({"ok": False, "error": "rows vacío"}, status=400)

        engine = get_engine()
        new_rows = []
        with engine.begin() as conn:
            cols_all = list_columns(conn, schema, table)
            pks = pk_columns(conn, schema, table)
            types_map_lc = get_column_types(conn, schema, table)

            returning = '*, ctid::text AS "_ctid"' if not pks else '*'

            for r in rows:
                cols_used = [c for c in cols_all if c in r]
                if not cols_used:
                    continue

                # normaliza valores por tipo
                params = {}
                for i, c in enumerate(cols_used):
                    try:
                        params[f"v{i}"] = coerce_value_for_type(types_map_lc.get(c), r[c])
                    except Exception as e:
                        return JsonResponse(
                            {"ok": False, "error": f"Valor inválido para columna '{c}' ({types_map_lc.get(c)}): {e}"},
                            status=400
                        )

                collist = ", ".join(qi(c) for c in cols_used)
                values = ", ".join(f":v{i}" for i in range(len(cols_used)))
                q = (
                    f'INSERT INTO {qi(schema)}.{qi(table)} ({collist}) '
                    f'VALUES ({values}) RETURNING {returning}'
                )
                res = conn.execute(text(q), params)
                row = dict(res.mappings().first())
                new_rows.append(row)

        return JsonResponse({"ok": True, "inserted": len(new_rows), "rows": new_rows})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
    
@login_required
@require_http_methods(["POST"])
def delete_rows(request, schema, table):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        keys = payload.get("keys") or []
        if not keys:
            return JsonResponse({"ok": False, "error": "keys vacío"}, status=400)

        engine = get_engine()
        with engine.begin() as conn:
            pks = pk_columns(conn, schema, table)
            deleted = 0
            for k in keys:
                params = {}
                if pks:
                    where = " AND ".join(f"{qi(col)} = :k{i}" for i, col in enumerate(pks))
                    for i, col in enumerate(pks):
                        params[f'k{i}'] = k[col]
                else:
                    where = "ctid = :k0"
                    params["k0"] = k["_ctid"]
                q = f'DELETE FROM {qi(schema)}.{qi(table)} WHERE {where}'
                conn.execute(text(q), params)
                deleted += 1
        return JsonResponse({"ok": True, "deleted": deleted})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def rename_columns(request, schema, table):
    """
    body: { "mapping": { "old_name": "new_name", ... } }
    Aplica ALTER TABLE ... RENAME COLUMN ... en Postgres.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        mapping = payload.get("mapping", {})
        if not mapping:
            return HttpResponseBadRequest("mapping requerido")

        engine = get_engine()
        with engine.begin() as conn:
            for old, new in mapping.items():
                conn.exec_driver_sql(
                    f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'RENAME COLUMN {quoted_ident(old)} TO {quoted_ident(new)}'
                )
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def cast_columns(request, schema, table):
    """
    body: { "types": { "col": "int|float|string|date|timestamp|numeric(10,2)" } }
    """
    type_map = {
        "int": "INTEGER",
        "float": "DOUBLE PRECISION",
        "string": "TEXT",
        "date": "DATE",
        "timestamp": "TIMESTAMP"
    }
    try:
        payload = json.loads(request.body.decode("utf-8"))
        types = payload.get("types", {})
        if not types:
            return HttpResponseBadRequest("types requerido")

        engine = get_engine()
        with engine.begin() as conn:
            for col, t in types.items():
                pgtype = type_map.get(t.lower(), t)  # permite tipos libres como numeric(10,2)
                conn.exec_driver_sql(
                    f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'ALTER COLUMN {quoted_ident(col)} TYPE {pgtype} USING {quoted_ident(col)}::{pgtype}'
                )
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def handle_nulls(request, schema, table):
    """
    body: { "action": "fill|drop", "value": "<literal>", "cols": ["col1","col2"] }
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        action = payload.get("action")
        cols = payload.get("cols", [])
        value = payload.get("value")

        if action not in ("fill", "drop"):
            return HttpResponseBadRequest("action inválida")

        engine = get_engine()
        with engine.begin() as conn:
            if action == "drop":
                # Borra filas si cualquier col seleccionada es NULL
                cond = " OR ".join([f"{quoted_ident(c)} IS NULL" for c in cols]) or "FALSE"
                conn.exec_driver_sql(
                    f'DELETE FROM {quoted_ident(schema)}.{quoted_ident(table)} WHERE {cond}'
                )
            else:  # fill
                if not cols:
                    return HttpResponseBadRequest("cols requerido")
                # value como literal (simple); para numéricos, frontend debería mandar 0 etc.
                sets = ", ".join([f'{quoted_ident(c)} = COALESCE({quoted_ident(c)}, :val)' for c in cols])
                conn.execute(
                    text(f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} SET {sets}'),
                    {"val": value}
                )
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def add_calculated(request, schema, table):
    """
    body: { "new_col": "ingreso_total", "expr": "precio * cantidad" }
    Crea nueva columna y la rellena con la expresión.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        new_col = payload.get("new_col")
        expr = payload.get("expr")
        if not new_col or not expr:
            return HttpResponseBadRequest("new_col y expr requeridos")

        engine = get_engine()
        with engine.begin() as conn:
            # Añade columna tipo DOUBLE PRECISION por defecto (puedes mejorar con inferencia)
            conn.exec_driver_sql(
                f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(table)} '
                f'ADD COLUMN IF NOT EXISTS {quoted_ident(new_col)} DOUBLE PRECISION'
            )
            conn.exec_driver_sql(
                f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} SET {quoted_ident(new_col)} = {expr}'
            )
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def aggregate_preview(request, schema, table):
    """
    body: { "group_by": ["colA","colB"], "metrics": [{"col":"ventas","op":"sum"}] }
    Devuelve filas agregadas (limit 200) para vista previa.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        group_by = payload.get("group_by", [])
        metrics = payload.get("metrics", [])  # lista de {col, op}

        if not group_by and not metrics:
            return HttpResponseBadRequest("group_by o metrics requeridos")

        sel_parts = []
        if group_by:
            sel_parts.extend([f"{quoted_ident(c)}" for c in group_by])
        for m in metrics:
            col = quoted_ident(m["col"])
            op = m["op"].upper()
            sel_parts.append(f"{op}({col}) AS {quoted_ident(op.lower()+'_'+m['col'])}")

        select_sql = ", ".join(sel_parts)
        group_sql = f" GROUP BY {', '.join([quoted_ident(c) for c in group_by])}" if group_by else ""
        sql = f'SELECT {select_sql} FROM {quoted_ident(schema)}.{quoted_ident(table)}{group_sql} LIMIT 200'

        engine = get_engine()
        with engine.begin() as conn:
            rows = conn.execute(text(sql)).fetchall()
            cols = rows[0].keys() if rows else []
            data = [dict(r._mapping) for r in rows]

        return JsonResponse({"ok": True, "columns": list(cols), "rows": data, "sql": sql})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def save_table(request, schema, table):
    """
    body: { "as": "replace|new", "new_name": "tabla_limpia" }
    Si 'replace' → crea copia y renombra atómico, o simplemente CREATE TABLE AS SELECT ... (según tu criterio).
    Aquí usa ‘CREATE TABLE new_name AS SELECT * FROM schema.table’.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        mode = payload.get("as", "new")
        new_name = payload.get("new_name")

        if mode == "new":
            if not new_name:
                return HttpResponseBadRequest("new_name requerido")
            engine = get_engine()
            with engine.begin() as conn:
                conn.exec_driver_sql(
                    f'CREATE TABLE {quoted_ident(schema)}.{quoted_ident(new_name)} AS '
                    f'SELECT * FROM {quoted_ident(schema)}.{quoted_ident(table)}'
                )
            return JsonResponse({"ok": True, "table": new_name})

        elif mode == "replace":
            # estrategia simple: crear temp, copiar, dropear original y renombrar
            tmp = f"{table}__tmp_copy"
            engine = get_engine()
            with engine.begin() as conn:
                conn.exec_driver_sql(
                    f'CREATE TABLE {quoted_ident(schema)}.{quoted_ident(tmp)} AS '
                    f'SELECT * FROM {quoted_ident(schema)}.{quoted_ident(table)}'
                )
                conn.exec_driver_sql(
                    f'DROP TABLE {quoted_ident(schema)}.{quoted_ident(table)} CASCADE'
                )
                conn.exec_driver_sql(
                    f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(tmp)} RENAME TO {quoted_ident(table)}'
                )
            return JsonResponse({"ok": True, "table": table})
        else:
            return HttpResponseBadRequest("modo inválido (use new|replace)")
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
    
@login_required
@require_http_methods(["POST"])
def nulls_action(request, schema, table):
    return handle_nulls(request, schema, table)

@login_required
@require_http_methods(["POST"])
def calc_newcol(request, schema, table):
    return add_calculated(request, schema, table)


ALLOWED_OPS = {
    "rename",            # {mapping:{old:new,...}}
    "cast",              # {types:{col:type,...}}
    "fill_nulls",        # {cols:[...], value:any}
    "drop_nulls",        # {cols:[...]}
    "add_calculated",    # {new_col:str, expr:str}
    "trim",              # {cols:[...]}
    "lower",             # {cols:[...]}
    "upper",             # {cols:[...]}
    "regex_replace",     # {col:str, pattern:str, repl:str}
}

def _schema_summary(conn, schema, table, sample_size=20):
    # columnas y tipos
    cols = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema=:s AND table_name=:t
        ORDER BY ordinal_position
    """), {"s": schema, "t": table}).fetchall()
    columns = [{"name": r[0], "type": r[1]} for r in cols]

    # muestra opcional
    sample = []
    if sample_size and sample_size > 0:
        res = conn.execute(text(
            f'SELECT * FROM {qi(schema)}.{qi(table)} LIMIT :n'
        ), {"n": sample_size})
        for row in res.mappings():
            sample.append(dict(row))

    return {"columns": columns, "sample": sample}

def _ai_prompt(schema, table, summary, guardrails):
    cols_text = "\n".join([f"- {c['name']}: {c['type']}" for c in summary["columns"]])
    return f"""
Eres un asistente de preparación de datos en PostgreSQL. Recibirás el esquema de una tabla y (opcional) una muestra.

SOLO puedes responder con un JSON con esta forma:
{{
  "intent": "string",
  "operations": [
    // Ejemplos válidos:
    {{"op":"trim","cols":["col1","col2"]}},
    {{"op":"lower","cols":["col1"]}},
    {{"op":"upper","cols":["col2"]}},
    {{"op":"regex_replace","col":"col1","pattern":"\\\\s+","repl":" "}},
    {{"op":"rename","mapping":{{"old":"new"}}}},
    {{"op":"cast","types":{{"col":"INTEGER|DOUBLE PRECISION|TEXT|DATE|TIME|TIMESTAMP|NUMERIC(10,2)"}}}},
    {{"op":"fill_nulls","cols":["c1","c2"],"value":"Desconocido"}},
    {{"op":"drop_nulls","cols":["c1"]}},
    {{
      "op":"add_calculated",
      "new_col":"duracion_minutos",
      "type":"DOUBLE PRECISION",
      "unit":"minutes",
      "expr":"EXTRACT(EPOCH FROM ((hora_fin - hora_inicio) + CASE WHEN hora_fin < hora_inicio THEN INTERVAL '24 hours' ELSE INTERVAL '0' END)) / 60.0"
    }},
    {{
      "op":"add_calculated",
      "new_col":"duracion_intervalo",
      "type":"INTERVAL",
      "expr":"(hora_fin - hora_inicio) + CASE WHEN hora_fin < hora_inicio THEN INTERVAL '24 hours' ELSE INTERVAL '0' END"
    }}
  ]
}}

REGLAS IMPORTANTES (PostgreSQL):
1) Si usas "add_calculated" con "type" NUMÉRICO (p. ej. "DOUBLE PRECISION", "NUMERIC", "REAL", "DECIMAL"), la "expr" DEBE ser NUMÉRICA. 
   - Para diferencias de tiempo, usa siempre: EXTRACT(EPOCH FROM (...))  → segundos.
   - Si "unit" = "minutes", divide entre 60.0; si "hours", entre 3600.0.
   - NUNCA uses "hora_fin - hora_inicio" directo si el "type" es numérico (eso devuelve INTERVAL).
2) Si "type" = "INTERVAL", entonces sí puedes usar "(hora_fin - hora_inicio)" (ajustando medianoche si aplica).
3) Considera cruce de medianoche: si "hora_fin" < "hora_inicio", suma INTERVAL '24 hours' al resultado.
4) Si las columnas de hora pudieran ser TEXT, castea con "::time" dentro de la expresión.
   Ej.: EXTRACT(EPOCH FROM ((hora_fin::time - hora_inicio::time) + ...)).
5) Usa solo las operaciones permitidas. No generes SQL arbitrario ni DDL fuera de estas operaciones.
6) Devuelve SOLO JSON, sin texto adicional.

Contexto del usuario (guardrails):
{guardrails or "(sin instrucciones adicionales)"}

Tabla objetivo: {schema}.{table}
Columnas:
{cols_text}

Devuelve SOLO JSON con esta forma:
{{
  "intent": "string corta explicando el objetivo",
  "operations": [
    {{"op":"cast","types":{{"hora_fin":"TIME"}}}},
    {{"op":"fill_nulls","cols":["dia_ren"],"value":"Desconocido"}},
    ...
  ]
}}

Si no hay nada que hacer, devuelve {{"intent":"sin cambios","operations":[]}}.
No añadas texto fuera del JSON.
""".strip()

def _llm_generate_plan(prompt, summary):
    api_key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"ok": False, "error": "Falta GEMINI_API_KEY en settings o env"}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Enviamos prompt y, si hay muestra, la anexamos como JSON aparte
    parts = [prompt]
    if summary.get("sample"):
        safe_sample = _jsonable(summary["sample"])
        parts.append(json.dumps({"sample": safe_sample}, ensure_ascii=False))


    resp = model.generate_content(parts)
    raw = getattr(resp, "text", "") or ""

    # intenta extraer JSON
    plan = None
    try:
        plan = json.loads(raw)
    except Exception:
        # si vino con texto extra, intenta recuperar bloque JSON más grande
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                plan = json.loads(raw[start:end+1])
        except Exception:
            pass

    if not isinstance(plan, dict):
        return {"ok": False, "error": "La IA no devolvió JSON válido", "raw": raw[:1000]}

    # normaliza
    plan.setdefault("intent", "")
    ops = plan.get("operations") or []
    if not isinstance(ops, list):
        ops = []
    # filtra a whitelist
    filtered = []
    for op in ops:
        if not isinstance(op, dict): 
            continue
        if op.get("op") in ALLOWED_OPS:
            filtered.append(op)
    plan["operations"] = filtered
    return {"ok": True, "plan": plan, "raw": raw[:1000]}

def _apply_plan(conn, schema, table, plan: dict):
    """
    Traduce el plan a acciones seguras usando tus helpers/SQL.
    Ejecuta todo dentro de la transacción abierta (conn).
    """
    def col_exists(cname):
        r = conn.execute(text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema=:s AND table_name=:t AND column_name=:c
        """), {"s": schema, "t": table, "c": cname}).fetchone()
        return bool(r)

    for op in plan.get("operations", []):
        kind = op.get("op")
        if kind == "rename":
            mapping = op.get("mapping") or {}
            # valida columnas
            valid = {old:new for old,new in mapping.items() if col_exists(old)}
            for old, new in valid.items():
                conn.exec_driver_sql(
                    f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'RENAME COLUMN {quoted_ident(old)} TO {quoted_ident(new)}'
                )

        elif kind == "cast":
            types = op.get("types") or {}
            for col, t in types.items():
                if not col_exists(col): 
                    continue
                conn.exec_driver_sql(
                    f'ALTER TABLE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'ALTER COLUMN {quoted_ident(col)} TYPE {t} USING {quoted_ident(col)}::{t}'
                )

        elif kind == "fill_nulls":
            cols = op.get("cols") or []
            if not cols: 
                continue
            sets = ", ".join([f'{quoted_ident(c)} = COALESCE({quoted_ident(c)}, :val)' for c in cols if col_exists(c)])
            if sets:
                conn.execute(text(
                    f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} SET {sets}'
                ), {"val": op.get("value")})

        elif kind == "drop_nulls":
            cols = [c for c in (op.get("cols") or []) if col_exists(c)]
            if cols:
                cond = " OR ".join([f"{quoted_ident(c)} IS NULL" for c in cols])
                conn.exec_driver_sql(
                    f'DELETE FROM {quoted_ident(schema)}.{quoted_ident(table)} WHERE {cond}'
                )

        elif kind == "add_calculated":
            new_col = op.get("new_col")
            expr = op.get("expr")
            desired_type = (op.get("type") or "").upper().strip()  # opcional
            unit = (op.get("unit") or "seconds").lower().strip()   # solo si numeric

            if not new_col or not expr:
                continue

            # Tipos actuales de columnas
            types_map = get_column_types(conn, schema, table)  # {col_lower: data_type}
            existing = types_map.get(new_col.lower())

            # Heurística: si no especificaron type y parece intervalo, marcamos INTERVAL;
            # si no, DOUBLE PRECISION.
            looks_interval = bool(
                re.search(r'\bage\s*\(', expr, re.I) or
                re.search(r'::\s*interval\b', expr, re.I) or
                re.search(r'\b(time|date|timestamp|hora|fecha)\b.*-.*\b(time|date|timestamp|hora|fecha)\b', expr, re.I)
            )
            if not desired_type:
                desired_type = "INTERVAL" if looks_interval else "DOUBLE PRECISION"

            # Si la columna no existe, créala con el tipo deseado
            if not existing:
                conn.exec_driver_sql(
                    f'ALTER TABLE {qi(schema)}.{qi(table)} '
                    f'ADD COLUMN IF NOT EXISTS {qi(new_col)} {desired_type}'
                )
                existing = desired_type.lower()

            # Prepara la expresión final según el tipo que tenga la columna realmente
            set_expr = expr

            if existing.startswith("double") or existing in ("numeric", "real", "double precision", "decimal"):
                # La columna es NUMÉRICA → si la expr luce intervalo, conviértela a EPOCH
                if looks_interval and not re.search(r'EXTRACT\s*\(\s*EPOCH', expr, re.I):
                    set_expr = f'EXTRACT(EPOCH FROM ({expr}))'
                    if unit == "minutes":
                        set_expr = f'({set_expr})/60.0'
                    elif unit == "hours":
                        set_expr = f'({set_expr})/3600.0'

            elif existing.startswith("interval"):
                # La columna es INTERVAL → usa la expr tal cual (debe devolver intervalo)
                pass

            elif existing == "text":
                # Como texto: castea a texto el resultado
                set_expr = f'({expr})::text'

            else:
                # Si el tipo existente no cuadra, intenta ajustarlo de forma segura.
                # Ej.: querían INTERVAL pero es DOUBLE → convierte a EPOCH
                if looks_interval and (existing.startswith("double") or existing in ("numeric","real","decimal")):
                    set_expr = f'EXTRACT(EPOCH FROM ({expr}))'

            # Aplica el UPDATE
            conn.exec_driver_sql(
                f'UPDATE {qi(schema)}.{qi(table)} SET {qi(new_col)} = {set_expr}'
            )

        elif kind == "trim":
            cols = [c for c in (op.get("cols") or []) if col_exists(c)]
            for c in cols:
                conn.exec_driver_sql(
                    f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'SET {quoted_ident(c)} = TRIM({quoted_ident(c)})'
                )

        elif kind == "lower":
            cols = [c for c in (op.get("cols") or []) if col_exists(c)]
            for c in cols:
                conn.exec_driver_sql(
                    f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'SET {quoted_ident(c)} = LOWER({quoted_ident(c)})'
                )

        elif kind == "upper":
            cols = [c for c in (op.get("cols") or []) if col_exists(c)]
            for c in cols:
                conn.exec_driver_sql(
                    f'UPDATE {quoted_ident(schema)}.{quoted_ident(table)} '
                    f'SET {quoted_ident(c)} = UPPER({quoted_ident(c)})'
                )

        elif kind == "regex_replace":
            col = op.get("col")
            pattern = op.get("pattern")
            repl = op.get("repl", "")
            if col and pattern and col_exists(col):
                conn.execute(
                    text(
                        f"UPDATE {qi(schema)}.{qi(table)} "
                        f"SET {qi(col)} = regexp_replace({qi(col)}::text, :pat, :rep, 'g')"
                    ),
                    {"pat": pattern, "rep": repl}
                )
        else:
            # ignorar no permitidos
            continue
 


@login_required
@require_POST
def ai_cleaning_suggest(request, schema, table):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        guardrails = payload.get("guardrails", "")
        sample_size = int(payload.get("sample_size", 20))
        mode = payload.get("mode", "suggest")

        engine = get_engine()
        with engine.begin() as conn:
            summary = _schema_summary(conn, schema, table, sample_size=sample_size)
            prompt = _ai_prompt(schema, table, summary, guardrails)
            out = _llm_generate_plan(prompt, summary)
            if not out.get("ok"):
                return JsonResponse(out, status=400)

            plan = out["plan"]
            plan = _normalize_plan(plan)

            if mode == "apply":
                _apply_plan(conn, schema, table, plan)
                return JsonResponse(_jsonable({"ok": True, "applied": True, "intent": plan.get("intent","")}))

            return JsonResponse(_jsonable({"ok": True, "plan": plan, "intent": plan.get("intent","")}))
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_POST
def ai_cleaning_apply(request, schema, table):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        plan = payload.get("plan")
        if not isinstance(plan, dict):
            return JsonResponse({"ok": False, "error": "plan inválido"}, status=400)

        # valida whitelist antes de aplicar
        ops = plan.get("operations") or []
        for op in ops:
            if not isinstance(op, dict) or op.get("op") not in ALLOWED_OPS:
                return JsonResponse({"ok": False, "error": f"Operación no permitida: {op}"}, status=400)

        engine = get_engine()
        with engine.begin() as conn:
            _apply_plan(conn, schema, table, plan)

        return JsonResponse({"ok": True, "applied": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

def _normalize_plan(plan):
    ops = plan.get("operations") or []
    for op in ops:
        if not isinstance(op, dict): 
            continue
        if op.get("op") == "add_calculated":
            t = (op.get("type") or "").upper()
            expr = op.get("expr", "")
            unit = (op.get("unit") or "seconds").lower()
            # si el type es numérico y la expr parece intervalo, convierte a epoch
            if t in ("DOUBLE PRECISION","NUMERIC","REAL","DECIMAL"):
                if re.search(r'\b-\b', expr) and not re.search(r'EXTRACT\s*\(\s*EPOCH', expr, re.I):
                    base = f"EXTRACT(EPOCH FROM ({expr}))"
                    if unit == "minutes":
                        op["expr"] = f"({base})/60.0"
                    elif unit == "hours":
                        op["expr"] = f"({base})/3600.0"
                    else:
                        op["expr"] = base
    return plan