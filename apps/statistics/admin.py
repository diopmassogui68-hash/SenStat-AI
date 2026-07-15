from django.contrib import admin
from .models import StatistiqueRegionale

@admin.register(StatistiqueRegionale)
class StatistiqueRegionaleAdmin(admin.ModelAdmin):
    list_display = ('region', 'annee', 'population')
    list_filter = ('annee', 'region')
    search_fields = ('region',)
