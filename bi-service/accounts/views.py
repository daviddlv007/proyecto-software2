# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm

def login_auto(request):
    """Auto-login para demos - acepta cualquier credencial"""
    if request.method == "POST":
        username = request.POST.get('username', 'demo')
        # Crear o obtener usuario
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('demo')
            user.save()
        # Login automático
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})
