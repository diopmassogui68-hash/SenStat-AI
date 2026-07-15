"""Vue API principale pour le traitement des questions en langage naturel."""
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
            result = QuestionService.process_question(question_text)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
