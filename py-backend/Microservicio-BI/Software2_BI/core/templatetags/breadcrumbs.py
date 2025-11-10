from django import template
from django.urls import reverse

register = template.Library()

def _route_key(context):
    match = context['request'].resolver_match
    if not match:
        return ""
    return f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name

def _url_from_target(target, view_kwargs):
    """
    target puede ser:
      - None  → sin link
      - "route_name" → reverse simple
      - ("route_name", ("kw1","kw2")) → usa kwargs del request
      - ("route_name", {"url_kw":"ctx_kw"}) → mapea nombres
    """
    if not target:
        return None
    if isinstance(target, str):
        return reverse(target)
    route_name, keys = target
    if isinstance(keys, (list, tuple)):
        kw = {k: view_kwargs[k] for k in keys if k in view_kwargs}
    elif isinstance(keys, dict):
        kw = {k: view_kwargs[v] for k, v in keys.items() if v in view_kwargs}
    else:
        kw = {}
    return reverse(route_name, kwargs=kw)

# Mapa declarativo. Puedes usar {schema} y {table} en los labels.
BREADCRUMB_MAP = {
    "prep:schema_index": [
        ("Inicio", "dashboard"),
        ("Editar base", None),
    ],
    "prep:picker": [
        ("Inicio", "dashboard"),
        ("Editar base", "prep:schema_index"),
        ("Tablas de {schema}", None),
    ],
    "prep:editor": [
        ("Inicio", "dashboard"),
        ("Editar base", "prep:schema_index"),
        ("Tablas", ("prep:picker", ("schema",))),  # ← linka usando el schema actual
        ("Editar {table}", None),
    ],
}

@register.inclusion_tag("includes/breadcrumbs.html", takes_context=True)
def show_breadcrumbs(context):
    match = context['request'].resolver_match
    key = _route_key(context)
    kwargs = match.kwargs if match else {}
    spec = BREADCRUMB_MAP.get(key)

    if not spec:
        # Fallback genérico
        label = key.split(":")[-1].replace("_", " ").title() if key else "Página"
        spec = [("Inicio", "dashboard"), (label, None)]

    trail = []
    for label, target in spec:
        # Render del label con kwargs (ej. "Editar {table}")
        try:
            label = label.format(**kwargs)
        except Exception:
            pass
        url = _url_from_target(target, kwargs) if target else None
        trail.append({"label": label, "url": url})

    return {"trail": trail}
