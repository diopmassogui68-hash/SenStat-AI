from django.test import TestCase
from apps.chatbot.nlp.intent_parser import parse_question, AmbiguousQueryError, OutOfScopeError
from apps.chatbot.nlp.entities import extract_years

class ChatbotTests(TestCase):
    def test_alias_indicateur(self):
        """Critère : Indicateurs (insensible casse/accents)."""
        intent1 = parse_question("Quel est le chômage à Dakar ?")
        intent2 = parse_question("donne moi le chomâge de dakar")
        self.assertEqual(intent1.indicator, "taux_chomage_pct")
        self.assertEqual(intent2.indicator, "taux_chomage_pct")

    def test_extraction_annees(self):
        """Critère : extraction d'années simples et de plages (évolution temporelle)."""
        intent = parse_question("Évolution de la population de 2020 à 2023")
        self.assertEqual(intent.start_year, 2020)
        self.assertEqual(intent.end_year, 2023)
        self.assertEqual(intent.operation, "trend")

    def test_ambiguite_comparaison(self):
        """Critère : les questions ambiguës ne déclenchent jamais une réponse inventée."""
        with self.assertRaises(AmbiguousQueryError):
            parse_question("Compare l'accès internet à Dakar.")

    def test_hors_perimetre(self):
        """Critère : question hors périmètre -> refus poli."""
        with self.assertRaises(OutOfScopeError):
            parse_question("Quel est le climat à Dakar ?")

    def test_deduction_operation(self):
        """Critère : Déduction correcte des opérations (classement top N, agrégation)."""
        intent_rank = parse_question("Top 3 des régions avec le plus de chômage")
        self.assertEqual(intent_rank.operation, "ranking")
        self.assertEqual(intent_rank.limit, 3)

        intent_sum = parse_question("Somme de la production céréalière en 2022")
        self.assertEqual(intent_sum.operation, "sum")
