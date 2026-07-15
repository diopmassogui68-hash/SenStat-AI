from django.test import TestCase
from apps.statistics.models import StatistiqueRegionale
from apps.statistics.services import StatistiqueService
from apps.chatbot.dto import QueryIntent

class StatistiqueServiceTests(TestCase):
    
    def setUp(self):
        # Création de données de test
        StatistiqueRegionale.objects.create(
            region="Dakar", annee=2024, population=4000000, 
            taux_urbanisation_pct=95, taux_alphabetisation_pct=85,
            taux_chomage_pct=15, taux_pauvrete_pct=10, acces_internet_pct=80,
            centres_sante=200, taux_scolarisation_pct=90, production_cerealiere_tonnes=10000
        )
        StatistiqueRegionale.objects.create(
            region="Thiès", annee=2024, population=2000000, 
            taux_urbanisation_pct=60, taux_alphabetisation_pct=70,
            taux_chomage_pct=10, taux_pauvrete_pct=20, acces_internet_pct=60,
            centres_sante=150, taux_scolarisation_pct=75, production_cerealiere_tonnes=50000
        )

    def test_orm_whitelist_security(self):
        """Test que la requête échoue si l'indicateur n'est pas dans la whitelist."""
        intent = QueryIntent(indicator="colonne_inexistante", operation="value")
        with self.assertRaises(ValueError) as context:
            StatistiqueService.execute_query(intent)
        self.assertTrue("Indicateur non autorisé" in str(context.exception))

    def test_orm_operation_compare(self):
        """Test de la comparaison entre deux régions."""
        intent = QueryIntent(
            indicator="taux_chomage_pct", 
            regions=["Dakar", "Thiès"], 
            operation="compare"
        )
        result = StatistiqueService.execute_query(intent)
        
        # On vérifie que la table contient bien 2 lignes et qu'elles sont ordonnées (Dakar 15% > Thiès 10%)
        self.assertEqual(len(result['table']), 2)
        self.assertEqual(result['table'][0]['region'], "Dakar")
        self.assertEqual(result['table'][1]['region'], "Thiès")
        self.assertIsNone(result['answer_value'])
