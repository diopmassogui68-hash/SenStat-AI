"""Tests unitaires pour le moteur NLP déterministe (chatbot)."""
from django.test import TestCase

from apps.chatbot.nlp.intent_parser import (
    AmbiguousQueryError,
    OutOfScopeError,
    parse_question,
)


class IndicateurTests(TestCase):
    """Tests sur la détection des indicateurs (insensible casse/accents)."""

    def test_synonyme_chomage(self) -> None:
        """Le mot 'chômage' (avec ou sans accent) doit mapper vers taux_chomage_pct."""
        intent1 = parse_question("Quel est le chômage à Dakar en 2024 ?")
        intent2 = parse_question("donne moi le chomage de dakar en 2024")
        self.assertEqual(intent1.indicator, "taux_chomage_pct")
        self.assertEqual(intent2.indicator, "taux_chomage_pct")

    def test_synonyme_internet(self) -> None:
        """Le mot 'internet' doit mapper vers acces_internet_pct."""
        intent = parse_question("Quel est l'accès internet à Kaolack en 2023 ?")
        self.assertEqual(intent.indicator, "acces_internet_pct")


class AnneeTests(TestCase):
    """Tests sur l'extraction des années et plages temporelles."""

    def test_plage_annees(self) -> None:
        """'de 2020 à 2023' doit extraire la plage et déduire l'opération trend."""
        intent = parse_question("Évolution de la population de 2020 à 2023")
        self.assertEqual(intent.start_year, 2020)
        self.assertEqual(intent.end_year, 2023)
        self.assertEqual(intent.operation, "trend")
        self.assertEqual(intent.chart_type, "line")

    def test_annee_simple(self) -> None:
        """'en 2022' doit extraire une seule année."""
        intent = parse_question("Population de Dakar en 2022")
        self.assertEqual(intent.start_year, 2022)
        self.assertEqual(intent.end_year, 2022)


class OperationTests(TestCase):
    """Tests sur la déduction des opérations."""

    def test_ranking_top_n(self) -> None:
        """'Top 3' doit déclencher l'opération ranking avec limit=3."""
        intent = parse_question("Top 3 des régions avec le plus de chômage")
        self.assertEqual(intent.operation, "ranking")
        self.assertEqual(intent.limit, 3)

    def test_somme(self) -> None:
        """'Somme' doit déclencher l'opération sum."""
        intent = parse_question("Somme de la production céréalière en 2022")
        self.assertEqual(intent.operation, "sum")

    def test_moyenne(self) -> None:
        """'Moyenne' doit déclencher l'opération average."""
        intent = parse_question("Moyenne du taux de chômage en 2024")
        self.assertEqual(intent.operation, "average")


class AmbiguiteTests(TestCase):
    """Tests sur la détection d'ambiguïté et les questions hors périmètre."""

    def test_comparaison_une_seule_region(self) -> None:
        """Demander une comparaison avec une seule région doit lever AmbiguousQueryError."""
        with self.assertRaises(AmbiguousQueryError):
            parse_question("Compare l'accès internet à Dakar en 2024.")

    def test_hors_perimetre(self) -> None:
        """Une question sans indicateur connu doit lever OutOfScopeError."""
        with self.assertRaises(OutOfScopeError):
            parse_question("Quel est le climat à Dakar ?")
