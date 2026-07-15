"""Configuration de l'application statistics (données statistiques régionales)."""
from django.apps import AppConfig


class StatisticsConfig(AppConfig):
    """Application Django pour le modèle StatistiqueRegionale et l'import CSV."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.statistics'
    verbose_name = 'Statistiques Régionales'
