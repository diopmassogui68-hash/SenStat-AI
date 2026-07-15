"""Configuration de l'interface d'administration pour les statistiques régionales."""
from django.contrib import admin
from .models import StatistiqueRegionale


@admin.register(StatistiqueRegionale)
class StatistiqueRegionaleAdmin(admin.ModelAdmin):
    """Admin enrichie pour la démonstration devant le jury."""

    list_display = (
        'region', 'annee', 'population',
        'taux_urbanisation_pct', 'taux_chomage_pct',
        'acces_internet_pct', 'taux_scolarisation_pct',
    )
    list_filter = ('annee', 'region')
    search_fields = ('region',)
    list_per_page = 20
    ordering = ('region', 'annee')
