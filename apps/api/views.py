from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.chatbot.ai.question_service import QuestionService
import logging

logger = logging.getLogger(__name__)

class QuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        
        if not text:
            return Response({"error": "Le champ 'text' est requis."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            service = QuestionService()
            response_data = service.process_question(text)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la question : {str(e)}", exc_info=True)
            return Response(
                {"error": "Une erreur interne s'est produite lors du traitement de votre demande."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
