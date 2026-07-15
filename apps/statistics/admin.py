from django.contrib import admin
from .models import StatistiqueRegionale

@admin.register(StatistiqueRegionale)
class StatistiqueRegionaleAdmin(admin.ModelAdmin):
    list_display = (
        'region', 'annee', 'population', 
        'taux_urbanisation_pct', 'taux_chomage_pct', 
        'acces_internet_pct'
    )
    list_filter = ('annee', 'region')
    search_fields = ('region',)
    ordering = ('region', 'annee')
