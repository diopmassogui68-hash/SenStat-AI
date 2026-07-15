"""Tests d'intégration pour l'endpoint API POST /api/question/."""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class QuestionApiTests(TestCase):
    """Tests sur le contrat JSON et la gestion d'erreurs de l'API."""

    def test_contrat_json_complet(self) -> None:
        """L'API doit retourner les 4 clés (answer, table, chart, metadata) sur une question valide."""
        url = reverse('api_question')
        response = self.client.post(
            url,
            data={'question': 'population de Dakar en 2024'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('answer', data)
        self.assertIn('table', data)
        self.assertIn('chart', data)
        self.assertIn('metadata', data)
        self.assertTrue(data['metadata']['fictitious'])

    def test_requete_sans_question(self) -> None:
        """Un POST sans le champ 'question' doit retourner 400."""
        url = reverse('api_question')
        response = self.client.post(
            url,
            data={},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_question_hors_perimetre(self) -> None:
        """Une question hors sujet doit retourner 200 avec un message de refus poli."""
        url = reverse('api_question')
        response = self.client.post(
            url,
            data={'question': 'Quel temps fait-il demain ?'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('answer', data)
        self.assertEqual(data['table'], [])
        self.assertIsNone(data['chart'])
