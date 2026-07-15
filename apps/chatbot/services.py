from typing import Dict, Any
from apps.chatbot.nlp.intent_parser import IntentParser
from apps.statistics.services import StatistiqueService

class QuestionService:
    """
    Orchestre le traitement complet d'une question.
    Sépare strictement la logique métier (NLP + ORM) de la logique HTTP (DRF).
    """

    @classmethod
    def process_question(cls, question_text: str) -> Dict[str, Any]:
        """
        Prend la question brute, extrait l'intention, l'exécute, et formate la réponse
        selon le contrat JSON exact exigé par le frontend.
        """
        # 1. Parsing NLP
        intent = IntentParser.parse(question_text)
        
        # 2. Gestion des cas d'erreur ou hors périmètre
        if intent.is_out_of_scope:
            return cls._build_response(
                answer="Je suis un assistant spécialisé dans les données statistiques du Sénégal (2020-2024). Je ne peux pas répondre à cette question.",
                table=[], chart=None, rows_used=0
            )
            
        if intent.is_ambiguous:
            return cls._build_response(
                answer=intent.ambiguity_reason or "Votre question est trop ambiguë, pouvez-vous la reformuler ?",
                table=[], chart=None, rows_used=0
            )
            
        # 3. Exécution de la requête ORM sécurisée
        try:
            db_result = StatistiqueService.execute_query(intent)
        except ValueError as e:
            return cls._build_response(
                answer=f"Désolé, je n'ai pas pu calculer ce résultat : {str(e)}",
                table=[], chart=None, rows_used=0
            )
            
        # 4. Construction de la réponse texte
        answer = cls._generate_text_answer(intent, db_result)
        
        # 5. Construction du format Chart.js
        chart_data = cls._build_chart_data(intent, db_result['table'])
        
        # 6. Format JSON final
        return cls._build_response(
            answer=answer,
            table=db_result['table'],
            chart=chart_data,
            rows_used=len(db_result['table']),
            intent=intent
        )
        
    @classmethod
    def _build_response(cls, answer: str, table: list, chart: dict, rows_used: int, intent=None) -> Dict[str, Any]:
        """Garantit le format exact du contrat JSON."""
        metadata = {
            "fictitious": True,
            "rows_used": rows_used
        }
        if intent:
            metadata["intent_debug"] = {
                "indicator": intent.indicator,
                "regions": intent.regions,
                "start_year": intent.start_year,
                "end_year": intent.end_year,
                "operation": intent.operation
            }
            
        return {
            "answer": answer,
            "table": table,
            "chart": chart,
            "metadata": metadata
        }

    @classmethod
    def _generate_text_answer(cls, intent, db_result) -> str:
        """Génère une réponse textuelle lisible."""
        val = db_result.get('answer_value')
        indicator_name = intent.indicator.replace('_pct', ' (%)').replace('_', ' ').capitalize() if intent.indicator else "l'indicateur"
        
        if not db_result['table'] and val is None:
            return "Aucune donnée disponible pour cette requête."
            
        if intent.operation == "value":
            region = db_result['table'][0]['region']
            annee = db_result['table'][0]['annee']
            return f"En {annee}, {indicator_name} pour {region} était de {val}."
            
        if intent.operation == "compare":
            return f"Voici la comparaison de {indicator_name} entre les régions demandées."
            
        if intent.operation == "trend":
            region = intent.regions[0] if intent.regions else "la région"
            return f"Voici l'évolution de {indicator_name} pour {region} de {intent.start_year} à {intent.end_year}."
            
        if intent.operation == "ranking":
            return f"Voici le classement concernant {indicator_name}."
            
        if intent.operation in ["sum", "average"]:
            op_fr = "La somme" if intent.operation == "sum" else "La moyenne"
            return f"{op_fr} de {indicator_name} pour votre sélection est de {val:.2f}."
            
        return "Voici les résultats de votre recherche."

    @classmethod
    def _build_chart_data(cls, intent, table_data: list) -> Optional[Dict[str, Any]]:
        """Prépare le payload exact pour Chart.js selon le contrat."""
        if not intent.chart_type or not table_data or intent.operation in ["sum", "average"]:
            return None
            
        # Pour le graphique "trend" (ligne temporel)
        if intent.operation == "trend":
            labels = [str(row['annee']) for row in table_data]
            data = [row[intent.indicator] for row in table_data]
            return {
                "type": intent.chart_type,
                "labels": labels,
                "datasets": [{
                    "label": intent.indicator.replace('_', ' ').capitalize(),
                    "data": data,
                    "borderColor": "rgb(75, 192, 192)",
                    "tension": 0.1
                }]
            }
            
        # Pour les graphiques "compare" ou "ranking" (barres par région)
        if intent.operation in ["compare", "ranking", "value"]:
            labels = [row['region'] for row in table_data]
            data = [row[intent.indicator] for row in table_data]
            return {
                "type": intent.chart_type,
                "labels": labels,
                "datasets": [{
                    "label": intent.indicator.replace('_', ' ').capitalize(),
                    "data": data,
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgb(54, 162, 235)",
                    "borderWidth": 1
                }]
            }
            
        return None
