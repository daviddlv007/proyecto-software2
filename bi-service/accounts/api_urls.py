from django.urls import path
from .api_views import login_api 

urlpatterns = [
    path('login/', login_api, name='api_login'),
]
