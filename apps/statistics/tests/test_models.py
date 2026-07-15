from django.test import TestCase
from django.db import IntegrityError
from apps.statistics.models import StatistiqueRegionale
from django.core.exceptions import ValidationError

class StatistiqueModelTests(TestCase):
    
    def test_unicite_region_annee(self):
        """Test de la contrainte d'unicité sur le couple region + annee."""
        StatistiqueRegionale.objects.create(
            region="Dakar", annee=2024, population=1000, 
            taux_urbanisation_pct=50, taux_alphabetisation_pct=50,
            taux_chomage_pct=10, taux_pauvrete_pct=10, acces_internet_pct=50,
            centres_sante=10, taux_scolarisation_pct=50, production_cerealiere_tonnes=1000
        )
        
        # Tenter d'insérer le même couple doit échouer
        with self.assertRaises(IntegrityError):
            StatistiqueRegionale.objects.create(
                region="Dakar", annee=2024, population=2000, 
                taux_urbanisation_pct=60, taux_alphabetisation_pct=60,
                taux_chomage_pct=20, taux_pauvrete_pct=20, acces_internet_pct=60,
                centres_sante=20, taux_scolarisation_pct=60, production_cerealiere_tonnes=2000
            )

    def test_validation_pourcentage(self):
        """Test que les pourcentages invalides (>100) sont rejetés."""
        stat = StatistiqueRegionale(
            region="Thiès", annee=2024, population=1000, 
            taux_urbanisation_pct=150.0, # Invalide
            taux_alphabetisation_pct=50, taux_chomage_pct=10, 
            taux_pauvrete_pct=10, acces_internet_pct=50,
            centres_sante=10, taux_scolarisation_pct=50, production_cerealiere_tonnes=1000
        )
        with self.assertRaises(ValidationError):
            stat.full_clean()
