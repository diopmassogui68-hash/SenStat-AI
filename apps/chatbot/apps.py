"""Configuration de l'application chatbot (NLP et IA générative)."""
from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    """Application Django pour l'analyse NLP et l'intégration Gemini."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chatbot'
    verbose_name = 'Chatbot NLP'
