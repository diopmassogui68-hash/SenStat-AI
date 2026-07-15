from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class StatistiqueRegionale(models.Model):
    region = models.CharField(max_length=100)
    annee = models.IntegerField()
    population = models.IntegerField()
    taux_urbanisation_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    taux_alphabetisation_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    taux_chomage_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    taux_pauvrete_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    acces_internet_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    centres_sante = models.IntegerField()
    taux_scolarisation_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    production_cerealiere_tonnes = models.FloatField()

    class Meta:
        unique_together = ('region', 'annee')
        verbose_name = "Statistique Régionale"
        verbose_name_plural = "Statistiques Régionales"

    def __str__(self):
        return f"{self.region} - {self.annee}"
