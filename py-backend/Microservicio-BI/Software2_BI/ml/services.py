import os, json
import pandas as pd
import numpy as np
from datetime import datetime
from django.conf import settings
from sqlalchemy import text

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, r2_score, mean_absolute_error, mean_squared_error, roc_curve
import joblib

from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

from ingestion.services import get_engine

class DateFeaturizer(BaseEstimator, TransformerMixin):
    def __init__(self, dt_cols=None):
        self.dt_cols = dt_cols

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.dt_cols is None:
            return pd.DataFrame(index=X.index)

        cols = list(self.dt_cols)  # copia segura (aquí sí)
        if not isinstance(X, pd.DataFrame):
            raise ValueError("DateFeaturizer requiere DataFrame (con nombres de columnas).")

        out = pd.DataFrame(index=X.index)
        for c in cols:
            # soporta date/timestamp/time guardados como texto
            s = pd.to_datetime(X[c].astype(str), errors="coerce")
            out[c+"_year"]   = s.dt.year
            out[c+"_month"]  = s.dt.month
            out[c+"_day"]    = s.dt.day
            out[c+"_dow"]    = s.dt.dayofweek
            out[c+"_hour"]   = s.dt.hour
            out[c+"_minute"] = s.dt.minute
        return out

    def get_feature_names_out(self, input_features=None):
        cols = list(self.dt_cols or [])
        feats = []
        for c in cols:
            feats += [f"{c}_year", f"{c}_month", f"{c}_day", f"{c}_dow", f"{c}_hour", f"{c}_minute"]
        return np.array(feats, dtype=object)

# Reutiliza tu engine/quote:

def qi(s): return '"' + s.replace('"', '""') + '"'

# ---------- almacenamiento de modelos ----------
def _store_dir():
    base = getattr(settings, "MEDIA_ROOT", None) or os.path.join(os.getcwd(), "media")
    d = os.path.join(base, "ml_models")
    os.makedirs(d, exist_ok=True)
    return d

# ---------- utilidades ----------
def _infer_task(y: pd.Series, explicit: str|None) -> str:
    if explicit in ("classification", "regression"): return explicit
    # heurística simple
    if y.dtype == "O" or y.dtype == "bool" or y.nunique(dropna=True) <= 20:
        return "classification"
    return "regression"

def _split(df: pd.DataFrame, target: str, time_col: str|None, test_pct: int):
    if time_col and time_col in df.columns:
        df = df.dropna(subset=[time_col]).copy()
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df = df.dropna(subset=[time_col]).sort_values(time_col)
        k = max(1, int(len(df)*(100-test_pct)/100))
        return df.iloc[:k], df.iloc[k:]
    X = df.drop(columns=[target]); y = df[target]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_pct/100.0, random_state=42, shuffle=True)
    return pd.concat([Xtr, ytr], axis=1), pd.concat([Xte, yte], axis=1)

def _build_pipeline(X: pd.DataFrame, task: str, algo: str):
    num_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]

    # detecta columnas de fecha/hora (incluye objetos que parecen fechas u horas)
    dt_cols = [c for c in X.columns if (
        pd.api.types.is_datetime64_any_dtype(X[c]) or
        "date" in str(X[c].dtype).lower() or
        "time" in str(X[c].dtype).lower()
    )]

    # categóricas = texto/categorical PERO excluyendo dt_cols y num_cols
    cat_cols = [c for c in X.columns
                if (pd.api.types.is_string_dtype(X[c]) or pd.api.types.is_categorical_dtype(X[c]))
                and c not in dt_cols and c not in num_cols]

    transformers = []
    if num_cols:
        transformers.append((
            "num",
            Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc",  StandardScaler()),
            ]),
            num_cols
        ))
    if cat_cols:
        transformers.append((
            "cat",
            Pipeline([
                ("imp", SimpleImputer(strategy="most_frequent")),
                ("oh",  OneHotEncoder(handle_unknown="ignore")),
            ]),
            cat_cols
        ))
    if dt_cols:
        transformers.append((
            "dt",
            Pipeline([
                ("fe",  DateFeaturizer(dt_cols=dt_cols)),  # 👈 param intacto
                ("imp", SimpleImputer(strategy="median")),
                ("sc",  StandardScaler()),
            ]),
            dt_cols  # 👈 el ColumnTransformer le pasa solo estas columnas
        ))

    pre = ColumnTransformer(transformers=transformers, remainder="drop")

    if task == "classification":
        if algo == "rf":  model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
        elif algo == "hgb": model = HistGradientBoostingClassifier(random_state=42)
        elif algo == "logreg": model = LogisticRegression(max_iter=1000)
        else: model = HistGradientBoostingClassifier(random_state=42)
    else:
        if algo == "rf":  model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
        elif algo == "hgb": model = HistGradientBoostingRegressor(random_state=42)
        elif algo == "ridge": model = Ridge(alpha=1.0)
        else: model = HistGradientBoostingRegressor(random_state=42)

    return Pipeline([("pre", pre), ("model", model)])

def _metrics(task, y_true, y_pred, proba=None):
    if task == "classification":
        out = {"accuracy": float(accuracy_score(y_true, y_pred)),
               "f1_macro": float(f1_score(y_true, y_pred, average="macro"))}
        if proba is not None and getattr(proba, "ndim", 1) == 2 and proba.shape[1] >= 2 and pd.Series(y_true).nunique()==2:
            try: out["roc_auc"] = float(roc_auc_score(y_true, proba[:,1]))
            except: pass
        return out
    return {"rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2":  float(r2_score(y_true, y_pred))}

# ---------- gráficos (Chart.js JSON) ----------
def _chart_reg_scatter(y_true, y_pred):
    s1, s2 = pd.Series(y_true), pd.Series(y_pred)
    mask = s1.notna() & s2.notna()
    if not mask.any(): return None
    yt, yp = s1[mask].astype(float), s2[mask].astype(float)
    mn, mx = float(min(yt.min(), yp.min())), float(max(yt.max(), yp.max()))
    return {
        "chart_type":"scatter","title":"Real vs Predicción",
        "data":{"datasets":[
            {"label":"Pred vs Real","data":[{"x":float(a),"y":float(p)} for a,p in zip(yt,yp)]},
            {"label":"y = x","data":[{"x":mn,"y":mn},{"x":mx,"y":mx}],"showLine":True,"pointRadius":0}
        ]}
    }

def _chart_reg_residuals(y_true, y_pred, bins=20):
    s1, s2 = pd.Series(y_true), pd.Series(y_pred)
    mask = s1.notna() & s2.notna()
    if not mask.any(): return None
    resid = (s2[mask].astype(float) - s1[mask].astype(float)).values
    hist, edges = np.histogram(resid, bins=bins)
    labels = [f"{edges[i]:.2f}–{edges[i+1]:.2f}" for i in range(len(edges)-1)]
    return {"chart_type":"bar","title":"Histograma de residuales (pred - real)",
            "data":{"labels":labels,"datasets":[{"label":"frecuencia","data":hist.astype(int).tolist()}]}}

def _chart_reg_over_time(df, time_col, y_true_col, y_pred_col):
    if not time_col or time_col not in df.columns: return None
    d = df[[time_col, y_true_col, y_pred_col]].dropna().copy()
    if d.empty: return None
    d[time_col] = pd.to_datetime(d[time_col], errors="coerce")
    d = d.dropna(subset=[time_col]).sort_values(time_col)
    labels = d[time_col].dt.strftime("%Y-%m-%d %H:%M").tolist()
    return {"chart_type":"line","title":"Serie temporal: real vs. pred",
            "data":{"labels":labels,"datasets":[
                {"label":"real","data":d[y_true_col].astype(float).tolist()},
                {"label":"pred","data":d[y_pred_col].astype(float).tolist()}
            ]}}

def _chart_cls_class_bar(y_true, y_pred):
    s_true, s_pred = pd.Series(y_true).astype(str), pd.Series(y_pred).astype(str)
    classes = sorted(set(s_true.unique()) | set(s_pred.unique()))
    counts = {c: {"real": int((s_true==c).sum()), "pred": int((s_pred==c).sum())} for c in classes}
    return {"chart_type":"bar","title":"Distribución por clase (real vs pred)",
            "data":{"labels":classes,"datasets":[
                {"label":"real","data":[counts[c]["real"] for c in classes]},
                {"label":"pred","data":[counts[c]["pred"] for c in classes]},
            ]}}

def _chart_cls_roc(y_true, proba):
    y = pd.Series(y_true)
    if proba is None or getattr(proba, "ndim", 1) != 2 or proba.shape[1]<2 or y.nunique()!=2: return None
    classes = sorted(y.dropna().unique())
    ybin = (y == classes[-1]).astype(int)
    fpr, tpr, _ = roc_curve(ybin, proba[:,1])
    return {"chart_type":"line","title":"ROC (binario)",
            "data":{"datasets":[
                {"label":"ROC","data":[{"x":float(a),"y":float(b)} for a,b in zip(fpr,tpr)],"showLine":True,"pointRadius":0},
                {"label":"azar","data":[{"x":0,"y":0},{"x":1,"y":1}],"showLine":True,"pointRadius":0}
            ]}}

def build_prediction_charts(df, target, pred_col, task, time_col=None, proba=None):
    charts = []
    if pred_col is None and "___pred___" in df.columns: pred_col = "___pred___"
    if target not in df.columns or pred_col not in df.columns: return charts
    if task == "regression":
        for fn in (_chart_reg_scatter, _chart_reg_residuals, lambda y, p: _chart_reg_over_time(df, time_col, target, pred_col)):
            c = fn(df[target], df[pred_col]) if fn!=_chart_reg_over_time else fn(None,None)
            if c: charts.append(c)
    else:
        c1 = _chart_cls_class_bar(df[target], df[pred_col]); c1 and charts.append(c1)
        c2 = _chart_cls_roc(df[target], proba);              c2 and charts.append(c2)
    return charts

# ---------- API de servicio ----------
def get_columns(schema, table):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema=:s AND table_name=:t
            ORDER BY ordinal_position
        """), {"s": schema, "t": table}).fetchall()
    return [{"name": r[0], "type": r[1]} for r in rows]

def _split(df: pd.DataFrame, target: str, time_col: str | None, test_pct: int):
    df = df.copy()

    # 1) quitar filas sin target
    if target in df.columns:
        df = df[~pd.isna(df[target])]

    n = len(df)
    if n == 0:
        # sin datos, devolvemos vacíos (el caller dará un error claro)
        return df, df.iloc[0:0]

    # 2) split temporal si es viable (>=2 filas válidas de tiempo)
    if time_col and time_col in df.columns:
        tmp = df.copy()
        tmp[time_col] = pd.to_datetime(tmp[time_col], errors="coerce")
        tmp = tmp.dropna(subset=[time_col])
        if len(tmp) >= 2:
            tmp = tmp.sort_values(time_col)
            k = int(len(tmp) * (100 - int(test_pct)) / 100)
            # asegurar al menos 1 en train y 1 en test
            k = max(1, min(k, len(tmp) - 1))
            tr = tmp.iloc[:k]
            te = tmp.iloc[k:]
            return tr, te
        # si no hay suficientes timestamps válidos, caemos a split aleatorio

    # 3) split aleatorio robusto
    if len(df) == 1:
        # 1 muestra: todo train, test vacío
        return df, df.iloc[0:0]

    X = df.drop(columns=[target])
    y = df[target]
    # garantizar que test tenga al menos 1 fila
    test_size = max(1, int(round(len(df) * (int(test_pct) / 100.0))))
    test_size = min(test_size, len(df) - 1)  # deja al menos 1 en train

    Xtr, Xte, ytr, yte = train_test_split(
        X, y,
        test_size=test_size,
        random_state=42,
        shuffle=True,
        stratify=(y if y.nunique() > 1 and len(y) >= 10 else None)
    )
    return pd.concat([Xtr, ytr], axis=1), pd.concat([Xte, yte], axis=1)

def train_model(schema, table, *, target, task, time_col, test_size, algo, features):
    engine = get_engine()
    with engine.begin() as conn:
        df = pd.read_sql(text(f'SELECT * FROM {qi(schema)}.{qi(table)}'), conn)

    if target not in df.columns:
        raise ValueError(f"Target '{target}' no existe")

    # seleccionar features
    if features:
        used = [c for c in features if c in df.columns and c != target]
    else:
        used = [c for c in df.columns if c != target]

    if not used:
        raise ValueError("No hay features para entrenar (lista vacía tras validar columnas).")

    X = df[used].copy()

    # intento suave de parseo fechas
    for c in X.columns:
        if X[c].dtype == object:
            try:
                X[c] = pd.to_datetime(X[c], errors='ignore')
            except:
                pass

    df_all = pd.concat([X, df[target]], axis=1)

    # === SPLIT ROBUSTO ===
    tr, te = _split(df_all, target, time_col, int(test_size))

    if len(tr) == 0:
        raise ValueError("No hay filas suficientes para entrenar (posible time_col sin fechas válidas o target todo nulo).")

    Xtr, ytr = tr.drop(columns=[target]), tr[target]
    Xte, yte = (te.drop(columns=[target]), te[target]) if len(te) else (te, te)

    # inferir tarea
    task_final = _infer_task(ytr, task)

    # checar clases si es clasificación
    if task_final == "classification" and pd.Series(ytr).nunique() < 2:
        raise ValueError("El target tiene una sola clase en el conjunto de entrenamiento; no se puede entrenar un clasificador.")

    pipe = _build_pipeline(Xtr, task_final, algo)
    pipe.fit(Xtr, ytr)

    # métricas: solo si hay test
    if len(Xte) > 0:
        if task_final == "classification":
            ypred = pipe.predict(Xte)
            try:
                proba = pipe.predict_proba(Xte)
            except:
                proba = None
            metrics = _metrics(task_final, yte, ypred, proba)
        else:
            ypred = pipe.predict(Xte)
            metrics = _metrics(task_final, yte, ypred)
    else:
        metrics = {"note": "Sin conjunto de prueba (muy pocos datos o time_col inválida)."}

    mid  = f"{schema}__{table}__{target}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    path = os.path.join(_store_dir(), f"{mid}.joblib")
    joblib.dump({
        "pipeline": pipe,
        "task": task_final,
        "target": target,
        "features": list(Xtr.columns),
        "time_col": time_col
    }, path)
    return {"model_id": mid, "metrics": metrics, "used_features": used}


def predict_model(schema, table, *, model_id, write_back_col=None):
    path = os.path.join(_store_dir(), f"{model_id}.joblib")
    if not os.path.exists(path): raise FileNotFoundError("modelo no encontrado")

    bundle = joblib.load(path)
    pipe, target, feats, task, time_col = bundle["pipeline"], bundle["target"], bundle["features"], bundle["task"], bundle.get("time_col")

    engine = get_engine()
    with engine.begin() as conn:
        df = pd.read_sql(text(f'SELECT * FROM {qi(schema)}.{qi(table)}'), conn)

    X = df.reindex(columns=feats, fill_value=np.nan).copy()
    ypred = pipe.predict(X)
    proba = None
    if task == "classification":
        try: proba = pipe.predict_proba(X)
        except: pass

    # escribir a DB si piden
    out_col = None
    if write_back_col is not None:
        out_col = write_back_col or ("pred_"+target)
        with engine.begin() as conn:
            if task == "regression":
                conn.exec_driver_sql(f'ALTER TABLE {qi(schema)}.{qi(table)} ADD COLUMN IF NOT EXISTS {qi(out_col)} DOUBLE PRECISION')
            else:
                conn.exec_driver_sql(f'ALTER TABLE {qi(schema)}.{qi(table)} ADD COLUMN IF NOT EXISTS {qi(out_col)} TEXT')
            # estrategia __rowid si no hay PK
            conn.exec_driver_sql(f'ALTER TABLE {qi(schema)}.{qi(table)} ADD COLUMN IF NOT EXISTS "__rowid" BIGINT')
            conn.exec_driver_sql(
                f'UPDATE {qi(schema)}.{qi(table)} t SET "__rowid" = s.seq '
                f'FROM (SELECT ctid, row_number() over()::bigint-1 as seq FROM {qi(schema)}.{qi(table)}) s '
                f'WHERE t.ctid = s.ctid AND t."__rowid" IS NULL'
            )
            # temp-table + update
            raw = conn.connection.cursor()
            raw.execute(f'CREATE TEMP TABLE _tmp_pred("__rowid" BIGINT, "{out_col}" {"DOUBLE PRECISION" if task=="regression" else "TEXT"})')
            from psycopg2.extras import execute_values
            vals = list(enumerate(ypred.tolist()))
            execute_values(raw, f'INSERT INTO _tmp_pred("__rowid","{out_col}") VALUES %s', vals)
            raw.execute(f'UPDATE {qi(schema)}.{qi(table)} t SET "{out_col}" = p."{out_col}" FROM _tmp_pred p WHERE t."__rowid" = p."__rowid"')

    # charts (en memoria)
    temp = df.copy()
    col_pred = out_col or "___pred___"
    temp[col_pred] = ypred
    charts = build_prediction_charts(temp, target, col_pred, task, time_col=time_col, proba=proba)
    return {"n": len(df), "write_back_col": out_col, "charts": charts}
