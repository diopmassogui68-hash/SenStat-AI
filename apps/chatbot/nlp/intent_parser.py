from apps.chatbot.dto import QueryIntent
from .synonyms import normalize_text, find_indicator, find_operation
from .entities import extract_years, extract_regions, extract_limit

class IntentParsingError(Exception):
    pass

class AmbiguousQueryError(Exception):
    pass

class OutOfScopeError(Exception):
    pass

def parse_question(question: str) -> QueryIntent:
    """Transforme la question utilisateur brute en un QueryIntent structuré."""
    norm_text = normalize_text(question)

    # 1. Extraction de l'indicateur (obligatoire)
    indicator = find_indicator(norm_text)
    if not indicator:
        raise OutOfScopeError("Désolé, je ne gère pas cette donnée. Je connais la population, l'urbanisation, l'alphabétisation, le chômage, la pauvreté, l'accès internet, les centres de santé, la scolarisation et la production céréalière.")

    # 2. Extraction des régions
    regions = extract_regions(norm_text)
    
    # 3. Extraction des années
    start_year, end_year = extract_years(question)
    
    # 4. Extraction de l'opération
    operation = find_operation(norm_text)
    
    # Règles de déduction et d'ambiguïté
    if len(regions) > 1 and operation == "value":
        operation = "compare"
        
    if start_year and end_year and start_year != end_year and operation == "value":
        operation = "trend"
        
    if "comparer" in norm_text and len(regions) < 2:
        raise AmbiguousQueryError("Vous souhaitez comparer, mais vous n'avez mentionné qu'une seule région. Lesquelles voulez-vous comparer ?")

    limit = extract_limit(question)
    if limit is not None:
        operation = "ranking"

    # Type de graphique par défaut
    chart_type = "bar"
    if operation == "trend":
        chart_type = "line"
        
    return QueryIntent(
        indicator=indicator,
        regions=regions,
        start_year=start_year,
        end_year=end_year,
        operation=operation,
        limit=limit,
        chart_type=chart_type
    )
