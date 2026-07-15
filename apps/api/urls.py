from django.urls import path
from .views import QuestionAPIView

urlpatterns = [
    path('question/', QuestionAPIView.as_view(), name='api_question'),
]
