"""Configuration de l'application api (endpoint REST)."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Application Django exposant l'endpoint POST /api/question/."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API REST'
