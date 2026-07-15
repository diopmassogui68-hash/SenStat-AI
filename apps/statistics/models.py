"""
Modèle de données principal pour les statistiques régionales du Sénégal.
Correspond exactement au dictionnaire de données du cahier des charges.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class StatistiqueRegionale(models.Model):
    """Statistique socio-économique d'une région du Sénégal pour une année donnée.

    Contrainte d'unicité : un seul enregistrement par couple (region, annee).
    Les champs en pourcentage sont validés entre 0 et 100 au niveau du modèle.
    """

    region = models.CharField(max_length=100, verbose_name="Région")
    annee = models.IntegerField(verbose_name="Année")
    population = models.IntegerField(verbose_name="Population")
    taux_urbanisation_pct = models.FloatField(
        verbose_name="Taux d'urbanisation (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    taux_alphabetisation_pct = models.FloatField(
        verbose_name="Taux d'alphabétisation (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    taux_chomage_pct = models.FloatField(
        verbose_name="Taux de chômage (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    taux_pauvrete_pct = models.FloatField(
        verbose_name="Taux de pauvreté (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    acces_internet_pct = models.FloatField(
        verbose_name="Accès internet (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    centres_sante = models.IntegerField(verbose_name="Centres de santé")
    taux_scolarisation_pct = models.FloatField(
        verbose_name="Taux de scolarisation (%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    production_cerealiere_tonnes = models.FloatField(
        verbose_name="Production céréalière (tonnes)",
    )

    class Meta:
        unique_together = ('region', 'annee')
        ordering = ['region', 'annee']
        verbose_name = "Statistique Régionale"
        verbose_name_plural = "Statistiques Régionales"

    def __str__(self) -> str:
        return f"{self.region} — {self.annee}"
