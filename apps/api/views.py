"""Vue API principale pour le traitement des questions en langage naturel."""
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
import hashlib

from apps.chatbot.services import QuestionService

from .serializers import QuestionRequestSerializer, QuestionResponseSerializer


@method_decorator(csrf_exempt, name='dispatch')
class QuestionAPIView(APIView):
    """Endpoint POST /api/question/ — traite une question et retourne la réponse structurée.

    La vue reste fine (séparation des responsabilités) : elle délègue
    toute la logique métier au QuestionService.
    """

    @extend_schema(
        request=QuestionRequestSerializer,
        responses={200: QuestionResponseSerializer},
        description=(
            "Traite une question en langage naturel sur les statistiques "
            "régionales du Sénégal et retourne une réponse structurée "
            "(texte, tableau, graphique)."
        ),
    )
    def post(self, request, *args, **kwargs):
        """Traite la requête POST et retourne le contrat JSON."""
        serializer = QuestionRequestSerializer(data=request.data)
        if serializer.is_valid():
            question_text = serializer.validated_data['question']
            
            # Caching : Hash de la question (en minuscule pour ignorer la casse)
            cache_key = "question_" + hashlib.md5(question_text.lower().strip().encode('utf-8')).hexdigest()
            cached_result = cache.get(cache_key)
            
            if cached_result:
                # Ajouter un flag pour le debug/UI si besoin
                cached_result['metadata']['cached'] = True
                return Response(cached_result, status=status.HTTP_200_OK)
            
            result = QuestionService.process_question(question_text)
            
            # Mettre en cache pour 15 minutes (900 secondes)
            cache.set(cache_key, result, timeout=900)
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
