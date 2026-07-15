from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes
from apps.chatbot.services import QuestionService
from .serializers import QuestionRequestSerializer, QuestionResponseSerializer

class QuestionAPIView(APIView):
    """
    Endpoint principal du Chatbot IA Statistique.
    Accepte une question en texte libre et retourne une réponse structurée (JSON).
    """
    
    @extend_schema(
        request=QuestionRequestSerializer,
        responses={200: QuestionResponseSerializer},
        description="Traite une question en langage naturel sur les statistiques régionales sénégalaises.",
        examples=[
            OpenApiExample(
                'Évolution',
                value={'question': "Quelle est l'évolution du taux de chômage à Dakar ?"},
                request_only=True,
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = QuestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        question_text = serializer.validated_data['question']
        
        # Le service encapsule toute la logique métier et retourne un dictionnaire formaté
        response_data = QuestionService.process_question(question_text)
        
        return Response(response_data, status=status.HTTP_200_OK)
