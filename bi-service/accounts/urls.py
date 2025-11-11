# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view
from .forms import LoginForm

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.login_auto, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup_view, name="signup"),
]
