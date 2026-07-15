import os
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from apps.statistics.models import StatistiqueRegionale

class ImportCommandTests(TestCase):
    
    def setUp(self):
        # Création d'un petit fichier CSV de test temporaire
        self.csv_path = os.path.join(settings.BASE_DIR, 'test_data.csv')
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write("region,annee,population,taux_urbanisation_pct,taux_alphabetisation_pct,taux_chomage_pct,taux_pauvrete_pct,acces_internet_pct,centres_sante,taux_scolarisation_pct,production_cerealiere_tonnes\n")
            f.write("Dakar,2020,3920000,97.2,80.5,14.8,9.1,74,138,91,18324\n")
            f.write("Dakar,2021,4000000,97.5,81.0,14.5,9.0,76,140,92,18500\n")

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_import_idempotence(self):
        """Test que la commande d'import est idempotente (ne crée pas de doublons)."""
        # Premier import
        call_command('importer_statistiques', self.csv_path)
        count_first = StatistiqueRegionale.objects.count()
        self.assertEqual(count_first, 2)
        
        # Deuxième import du même fichier
        call_command('importer_statistiques', self.csv_path)
        count_second = StatistiqueRegionale.objects.count()
        self.assertEqual(count_second, 2) # Le nombre ne doit pas avoir augmenté
