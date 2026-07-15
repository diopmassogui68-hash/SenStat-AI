from django.db import models
from django.core.validators import MinValueValidator
from .validators import validate_percentage

class StatistiqueRegionale(models.Model):
    """
    Modèle représentant les statistiques d'une région sénégalaise pour une année donnée.
    Toutes les données de ce modèle dans le cadre du projet sont strictement fictives et 
    à vocation pédagogique.
    """
    region = models.CharField(max_length=100, verbose_name="Région")
    annee = models.IntegerField(verbose_name="Année")
    population = models.IntegerField(verbose_name="Population", validators=[MinValueValidator(0)])
    
    taux_urbanisation_pct = models.FloatField(
        verbose_name="Taux d'urbanisation (%)", 
        validators=[validate_percentage]
    )
    taux_alphabetisation_pct = models.FloatField(
        verbose_name="Taux d'alphabétisation (%)", 
        validators=[validate_percentage]
    )
    taux_chomage_pct = models.FloatField(
        verbose_name="Taux de chômage (%)", 
        validators=[validate_percentage]
    )
    taux_pauvrete_pct = models.FloatField(
        verbose_name="Taux de pauvreté (%)", 
        validators=[validate_percentage]
    )
    acces_internet_pct = models.FloatField(
        verbose_name="Accès internet (%)", 
        validators=[validate_percentage]
    )
    
    centres_sante = models.IntegerField(verbose_name="Centres de santé", validators=[MinValueValidator(0)])
    taux_scolarisation_pct = models.FloatField(
        verbose_name="Taux de scolarisation (%)", 
        validators=[validate_percentage]
    )
    production_cerealiere_tonnes = models.FloatField(
        verbose_name="Production céréalière (tonnes)", 
        validators=[MinValueValidator(0.0)]
    )

    class Meta:
        verbose_name = "Statistique Régionale"
        verbose_name_plural = "Statistiques Régionales"
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'annee'], 
                name='unique_region_annee'
            )
        ]
        ordering = ['region', 'annee']

    def __str__(self):
        return f"{self.region} ({self.annee})"
