from django.test import TestCase
from apps.chatbot.nlp.intent_parser import IntentParser
from apps.chatbot.nlp.entities import extract_years

class NLPTests(TestCase):
    
    def test_synonyms_and_alias(self):
        """Test que les synonymes (ex: habitants, sans emploi) mappent bien aux indicateurs."""
        intent1 = IntentParser.parse("Combien d'habitants à Dakar ?")
        self.assertEqual(intent1.indicator, "population")
        
        intent2 = IntentParser.parse("Le nombre de sans emploi à Thiès")
        self.assertEqual(intent2.indicator, "taux_chomage_pct")

    def test_extraction_annees(self):
        """Test de l'extraction des années 2020-2024."""
        start, end = extract_years("évolution de 2021 à 2023")
        self.assertEqual(start, 2021)
        self.assertEqual(end, 2023)
        
        # Test annee unique
        start2, end2 = extract_years("en 2024")
        self.assertEqual(start2, 2024)
        self.assertEqual(end2, 2024)

    def test_ambiguity_detection(self):
        """Test du rejet pour ambiguïté si l'indicateur n'est pas trouvé."""
        intent = IntentParser.parse("Quelle est la situation de Dakar en 2024 ?")
        self.assertTrue(intent.is_ambiguous)
        self.assertIsNotNone(intent.ambiguity_reason)

    def test_out_of_scope(self):
        """Test du refus poli pour les questions hors sujet (ex: sport)."""
        intent = IntentParser.parse("Quel est le score du match de football ?")
        self.assertTrue(intent.is_out_of_scope)

    def test_operation_deduction(self):
        """Test que l'opération est bien déduite du contexte si pas de mot-clé."""
        # Deux régions, pas de mot-clé "comparer" -> l'intention déduite doit être 'compare'
        intent = IntentParser.parse("Le chômage entre Dakar et Thiès")
        self.assertEqual(intent.operation, "compare")
