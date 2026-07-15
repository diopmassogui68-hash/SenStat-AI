"""Tests unitaires pour le module statistics (modèle + validateurs)."""
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.statistics.models import StatistiqueRegionale
from apps.statistics.validators import (
    ANNEE_MAX,
    ANNEE_MIN,
    nettoyer_region,
    valider_annee,
    valider_pourcentage,
)


class StatistiqueModeleTests(TestCase):
    """Tests sur le modèle StatistiqueRegionale."""

    def setUp(self) -> None:
        self.data = {
            "region": "Dakar", "annee": 2024, "population": 4000000,
            "taux_urbanisation_pct": 95, "taux_alphabetisation_pct": 85,
            "taux_chomage_pct": 10, "taux_pauvrete_pct": 8,
            "acces_internet_pct": 80, "centres_sante": 150,
            "taux_scolarisation_pct": 90, "production_cerealiere_tonnes": 10000,
        }

    def test_unicite_region_annee(self) -> None:
        """Un second import avec la même (region, annee) doit lever IntegrityError."""
        StatistiqueRegionale.objects.create(**self.data)
        self.assertEqual(StatistiqueRegionale.objects.count(), 1)
        with self.assertRaises(IntegrityError):
            StatistiqueRegionale.objects.create(**self.data)


class ValidateurTests(TestCase):
    """Tests sur les fonctions de validation métier."""

    def test_annee_dans_bornes(self) -> None:
        """Les années 2020-2024 sont valides, les autres non."""
        self.assertTrue(valider_annee(ANNEE_MIN))
        self.assertTrue(valider_annee(ANNEE_MAX))
        self.assertTrue(valider_annee(2022))
        self.assertFalse(valider_annee(2019))
        self.assertFalse(valider_annee(2025))

    def test_pourcentage_dans_bornes(self) -> None:
        """Les pourcentages doivent être entre 0 et 100 inclus."""
        self.assertTrue(valider_pourcentage(0.0))
        self.assertTrue(valider_pourcentage(100.0))
        self.assertTrue(valider_pourcentage(45.5))
        self.assertFalse(valider_pourcentage(-0.1))
        self.assertFalse(valider_pourcentage(100.1))

    def test_nettoyage_region_saint_louis(self) -> None:
        """nettoyer_region doit correctement gérer 'Saint-Louis'."""
        self.assertEqual(nettoyer_region("  saint-louis  "), "Saint-Louis")
        self.assertEqual(nettoyer_region("DAKAR"), "Dakar")
