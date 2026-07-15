from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import QuestionRequestSerializer, QuestionResponseSerializer
from apps.chatbot.services import QuestionService

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

@method_decorator(csrf_protect, name='dispatch')
class QuestionAPIView(APIView):
    @extend_schema(
        request=QuestionRequestSerializer,
        responses={200: QuestionResponseSerializer},
        description="Traite une question en langage naturel et retourne une réponse structurée (tableau, graphique)."
    )
    def post(self, request, *args, **kwargs):
        serializer = QuestionRequestSerializer(data=request.data)
        if serializer.is_valid():
            question_text = serializer.validated_data['question']
            
            # Appel de l'orchestrateur métier (Séparation des responsabilités respectée)
            result = QuestionService.process_question(question_text)
            
            # Retourne le contrat JSON strict exigé par le front-end
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
