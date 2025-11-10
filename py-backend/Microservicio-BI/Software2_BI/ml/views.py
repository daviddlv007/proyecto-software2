import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .services import get_columns, train_model, predict_model

@login_required
def panel(request, schema, table):
    return render(request, "ml/panel.html", {"schema": schema, "table": table})

@login_required
@require_http_methods(["GET"])
def config(request, schema, table):
    return JsonResponse({"columns": get_columns(schema, table)})

@login_required
@require_http_methods(["POST"])
def train(request, schema, table):
    try:
        p = json.loads(request.body.decode("utf-8"))
        out = train_model(
            schema, table,
            target=p.get("target"),
            task=p.get("task","auto"),
            time_col=p.get("time_col") or None,
            test_size=int(p.get("test_size",20)),
            algo=p.get("algo","auto"),
            features=p.get("features") or []
        )
        return JsonResponse({"ok": True, **out})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def predict(request, schema, table):
    try:
        p = json.loads(request.body.decode("utf-8"))
        out = predict_model(schema, table, model_id=p.get("model_id"), write_back_col=p.get("write_back_col", None))
        return JsonResponse({"ok": True, **out})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
