# accounts/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

def _extract_credentials(request):
    """
    Intenta extraer username/password de:
    1) JSON (Content-Type: application/json)
    2) Form-data o x-www-form-urlencoded (request.POST)
    """
    username = password = None

    # 1) JSON
    # request.body es bytes; si está vacío o no es JSON válido, seguimos al plan B
    if request.META.get("CONTENT_TYPE", "").startswith("application/json"):
        try:
            raw = request.body.decode("utf-8") if request.body else ""
            if raw:
                data = json.loads(raw)
                username = data.get("username")
                password = data.get("password")
        except Exception:
            # ignoramos y pasamos a POST
            pass

    # 2) Form
    if not username or not password:
        if request.method in ("POST", "PUT", "PATCH"):
            username = username or request.POST.get("username")
            password = password or request.POST.get("password")

    # saneamos
    if isinstance(username, str):
        username = username.strip()
    if isinstance(password, str):
        password = password.strip()

    return username, password

@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

    username, password = _extract_credentials(request)

    if not username or not password:
        return JsonResponse({
            "status": "error",
            "message": "Faltan credenciales. Envía 'username' y 'password' en JSON o form-data."
        }, status=400)

    # 1) Intento normal por username
    user = authenticate(username=username, password=password)

    # 2) Si no funcionó y parece email, intento por email
    if user is None and "@" in username:
        try:
            u = User.objects.get(email=username)
            if u.check_password(password) and u.is_active:
                user = u
        except User.DoesNotExist:
            pass

    if user is None:
        return JsonResponse({"status": "error", "message": "Credenciales inválidas"}, status=401)

    return JsonResponse({
        "status": "ok",
        "user": getattr(user, "username", None),
        "email": getattr(user, "email", None),
        "id": user.pk
    }, status=200)
