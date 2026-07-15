from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

class ApiTests(APITestCase):
    def test_api_reponse_format(self):
        """Critère : L'application fonctionne intégralement sans service IA externe (mode déterministe)."""
        url = reverse('api_question')
        data = {'question': 'population de Dakar en 2024'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Contrat JSON stable
        self.assertIn('answer', response.data)
        self.assertIn('table', response.data)
        self.assertIn('chart', response.data)
        self.assertIn('metadata', response.data)
        
    def test_api_requete_invalide(self):
        """Vérifie la gestion d'erreurs (champ manquant)."""
        url = reverse('api_question')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
