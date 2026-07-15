from apps.chatbot.nlp.intent_parser import parse_question, AmbiguousQueryError, OutOfScopeError, IntentParsingError
from apps.chatbot.ai.gemini_client import call_gemini
from apps.statistics.services import StatistiqueService
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    @staticmethod
    def process_question(question_text: str) -> dict:
        metadata = {"fictitious": True, "rows_used": 0, "ai_used": False}
        
        try:
            # 1. Tentative IA Générative (Bonus optionnel)
            intent = call_gemini(question_text)
            
            if intent:
                metadata["ai_used"] = True
                logger.info("Intention extraite par Gemini avec succès.")
            else:
                # 2. Repli déterministe (Obligatoire)
                logger.info("Utilisation du NLP déterministe de repli.")
                intent = parse_question(question_text)
            
            # 2. Requête ORM sécurisée
            answer, table_data, chart_data = StatistiqueService.execute_query(intent)
            
            # Nombre de lignes utilisées
            metadata["rows_used"] = len(table_data)
            
            # Format JSON attendu
            return {
                "answer": answer,
                "table": table_data,
                "chart": chart_data,
                "metadata": metadata
            }

        except AmbiguousQueryError as e:
            return {
                "answer": str(e),
                "table": [],
                "chart": None,
                "metadata": metadata
            }
        except OutOfScopeError as e:
            return {
                "answer": str(e),
                "table": [],
                "chart": None,
                "metadata": metadata
            }
        except ValueError as e:
            # Bloqué par la whitelist
            logger.error(f"Valeur invalide (whitelist) : {e}")
            return {
                "answer": "Je ne suis pas autorisé à répondre à cette question pour des raisons de sécurité.",
                "table": [],
                "chart": None,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")
            return {
                "answer": "Une erreur inattendue s'est produite lors de l'analyse de votre question.",
                "table": [],
                "chart": None,
                "metadata": metadata
            }
