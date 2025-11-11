from django.urls import path, include

urlpatterns = [
    path('', include('accounts.api_urls')),   # Rutas API de accounts
    path('', include('ingestion.urls')),      # Rutas API de ingestion
]
