"""
Orchestrateur métier : reçoit la question, produit la réponse JSON complète.

Ce service est le point d'entrée unique entre la vue API et la logique métier.
Il respecte la séparation des responsabilités : la vue DRF reste fine.
"""
import logging
from typing import Any

from apps.chatbot.ai.gemini_client import call_gemini
from apps.chatbot.nlp.intent_parser import (
    AmbiguousQueryError,
    OutOfScopeError,
    ChitChatError,
    parse_question,
)
from apps.statistics.services import StatistiqueService

logger = logging.getLogger(__name__)


class QuestionService:
    """Service d'orchestration bout-en-bout pour le traitement des questions.

    Flux :
      1. Tentative IA générative (Gemini) — bonus optionnel.
      2. Repli déterministe (NLP local) — obligatoire, garanti.
      3. Exécution ORM sécurisée via StatistiqueService.
      4. Construction de la réponse JSON conforme au contrat API.
    """

    @staticmethod
    def process_question(question_text: str) -> dict[str, Any]:
        """Traite une question utilisateur et retourne la réponse structurée.

        Args:
            question_text: La question brute en langage naturel.

        Returns:
            Dictionnaire conforme au contrat JSON de l'API :
            {answer, table, chart, metadata}.
        """
        metadata: dict[str, Any] = {
            "fictitious": True,
            "rows_used": 0,
            "ai_used": False,
        }

        try:
            # 1. Tentative IA générative (bonus optionnel)
            intent = call_gemini(question_text)

            if intent:
                metadata["ai_used"] = True
                logger.info("Intention extraite par Gemini avec succès.")
            else:
                # 2. Repli déterministe (obligatoire, garanti)
                logger.info("Utilisation du NLP déterministe.")
                intent = parse_question(question_text)

            # 3. Exécution ORM sécurisée
            answer, table_data, chart_data = StatistiqueService.execute_query(intent)

            metadata["rows_used"] = len(table_data)

            return {
                "answer": answer,
                "table": table_data,
                "chart": chart_data,
                "metadata": metadata,
            }

        except AmbiguousQueryError as e:
            return {
                "answer": str(e),
                "table": [],
                "chart": None,
                "metadata": metadata,
            }

        except OutOfScopeError as e:
            return {
                "answer": str(e),
                "table": [],
                "chart": None,
                "metadata": metadata,
            }

        except ChitChatError as e:
            return {
                "answer": str(e),
                "table": [],
                "chart": None,
                "metadata": metadata,
            }

        except ValueError as e:
            logger.error("Indicateur bloqué par la whitelist : %s", e)
            return {
                "answer": (
                    "Je ne suis pas autorisé à répondre à cette question "
                    "pour des raisons de sécurité."
                ),
                "table": [],
                "chart": None,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error("Erreur inattendue dans QuestionService : %s", e)
            return {
                "answer": (
                    "Une erreur inattendue s'est produite lors du traitement "
                    "de votre question. Veuillez reformuler."
                ),
                "table": [],
                "chart": None,
                "metadata": metadata,
            }
