from apps.chatbot.dto import QueryIntent
from .entities import (
    extract_regions, 
    extract_years, 
    extract_indicator, 
    extract_operation, 
    detect_out_of_scope,
    extract_limit
)

class IntentParser:
    """
    Analyseur déterministe pour convertir une question texte en un objet QueryIntent.
    Utilise des règles NLP simples (dictionnaires de synonymes et regex) pour 
    éviter toute dépendance lourde tout en garantissant des performances optimales.
    """
    
    @classmethod
    def parse(cls, question: str) -> QueryIntent:
        """
        Parse la question et retourne l'intention.
        Gère la détection d'ambiguïté et le hors-sujet.
        """
        intent = QueryIntent()
        
        # 1. Vérification du hors-sujet
        if detect_out_of_scope(question):
            intent.is_out_of_scope = True
            return intent
            
        # 2. Extraction des entités
        intent.regions = extract_regions(question)
        start_year, end_year = extract_years(question)
        intent.start_year = start_year
        intent.end_year = end_year
        
        intent.indicator = extract_indicator(question)
        intent.limit = extract_limit(question)
        
        num_years = 0
        if start_year and end_year:
            num_years = end_year - start_year + 1
            
        intent.operation = extract_operation(question, len(intent.regions), num_years)
        
        # 3. Détection d'ambiguïté
        cls._resolve_ambiguity(intent, question)
        
        # 4. Choix du type de graphique (si pertinent)
        cls._determine_chart_type(intent)
        
        return intent
        
    @classmethod
    def _resolve_ambiguity(cls, intent: QueryIntent, question: str):
        """
        Vérifie si la question est suffisamment précise pour être traitée.
        Définit is_ambiguous et ambiguity_reason si ce n'est pas le cas.
        """
        # Si aucun indicateur n'est trouvé, la question est ambiguë
        if not intent.indicator:
            intent.is_ambiguous = True
            intent.ambiguity_reason = "Je n'ai pas compris quel indicateur vous cherchez (ex: population, chômage, internet...)."
            return
            
        # Si on veut comparer mais qu'on a moins de 2 régions
        if intent.operation == "compare" and len(intent.regions) < 2:
            intent.is_ambiguous = True
            intent.ambiguity_reason = "Pour faire une comparaison, veuillez préciser au moins deux régions."
            return
            
        # Si on veut une évolution temporelle mais sans intervalle d'années défini
        if intent.operation == "trend" and intent.start_year == intent.end_year:
            # Par défaut, on pourrait prendre 2020-2024, mais c'est mieux d'assumer tout l'historique si on ne précise pas
            intent.start_year = 2020
            intent.end_year = 2024
            
    @classmethod
    def _determine_chart_type(cls, intent: QueryIntent):
        """
        Assigne le type de graphique le plus approprié à l'intention.
        """
        if intent.is_ambiguous or intent.is_out_of_scope:
            return
            
        if intent.operation == "trend":
            intent.chart_type = "line"
        elif intent.operation in ["compare", "ranking"]:
            intent.chart_type = "bar"
        elif intent.operation == "value" and len(intent.regions) > 1:
            intent.chart_type = "bar"
        else:
            intent.chart_type = None
