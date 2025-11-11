from django import template

register = template.Library()

@register.simple_tag
def ping():
    return "pong"

def _current_route(context):
    match = context['request'].resolver_match
    if not match:
        return ""
    return f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name

@register.simple_tag(takes_context=True)
def active_exact(context, *routes):
    """
    Devuelve clases 'active ...' si la ruta actual coincide exactamente
    con alguno de los nombres pasados (ej. 'dashboard', 'ingestion:list', etc.)
    """
    return "active bg-gradient-dark text-white" if _current_route(context) in routes else ""

@register.simple_tag(takes_context=True)
def active_namespace(context, *namespaces):
    """
    Marca activo por namespace (útil para agrupar secciones enteras).
    """
    match = context['request'].resolver_match
    ns = match.namespace if match else ""
    return "active bg-gradient-dark text-white" if ns in namespaces else ""
