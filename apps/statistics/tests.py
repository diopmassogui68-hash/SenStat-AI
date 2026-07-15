from django.test import TestCase
from apps.statistics.models import StatistiqueRegionale
from apps.statistics.validators import valider_annee, valider_pourcentage
from django.db.utils import IntegrityError

class StatistiqueTests(TestCase):
    def setUp(self):
        self.data = {
            "region": "Dakar", "annee": 2024, "population": 4000000, 
            "taux_urbanisation_pct": 95, "taux_alphabetisation_pct": 85, 
            "taux_chomage_pct": 10, "taux_pauvrete_pct": 8,
            "acces_internet_pct": 80, "centres_sante": 150, 
            "taux_scolarisation_pct": 90, "production_cerealiere_tonnes": 10000
        }

    def test_import_unicite(self):
        """Critère : un second import ne doit créer aucun doublon."""
        StatistiqueRegionale.objects.create(**self.data)
        self.assertEqual(StatistiqueRegionale.objects.count(), 1)
        
        with self.assertRaises(IntegrityError):
            StatistiqueRegionale.objects.create(**self.data)
            
    def test_validation_stricte(self):
        """Critère : toutes les valeurs de pourcentage validées entre 0 et 100 + années 2020-2024."""
        self.assertTrue(valider_annee(2022))
        self.assertFalse(valider_annee(2019)) # Hors borne inf
        self.assertFalse(valider_annee(2025)) # Hors borne sup
        
        self.assertTrue(valider_pourcentage(45.5))
        self.assertFalse(valider_pourcentage(-5))
        self.assertFalse(valider_pourcentage(105))
