"""
Parseur d'intention déterministe (mode de repli obligatoire).

Transforme une question en langage naturel en un objet QueryIntent structuré,
sans recours à un modèle IA. Ce module est le cœur du NLP et doit fonctionner
de manière autonome (critère du barème : fonctionnement sans IA externe).
"""
from apps.chatbot.dto import QueryIntent
from .synonyms import normalize_text, find_indicator, find_operation
from .entities import extract_years, extract_regions, extract_limit


class IntentParsingError(Exception):
    """Erreur générique lors de l'analyse de la question."""


class AmbiguousQueryError(Exception):
    """La question est ambiguë et nécessite une clarification de l'utilisateur."""


class OutOfScopeError(Exception):
    """La question porte sur un sujet non couvert par le jeu de données."""


class ChitChatError(Exception):
    """La question est une simple salutation ou conversationnelle."""


def parse_question(question: str) -> QueryIntent:
    """Transforme une question en langage naturel en QueryIntent structuré.

    Applique les règles de déduction dans l'ordre :
      1. Extraction de l'indicateur (obligatoire, sinon OutOfScopeError).
      2. Extraction des régions.
      3. Extraction des années.
      4. Détection de l'opération.
      5. Règles de déduction automatique (multi-région → compare, plage → trend).
      6. Détection d'ambiguïté (compare avec < 2 régions → AmbiguousQueryError).

    Args:
        question: La question brute de l'utilisateur.

    Returns:
        Un QueryIntent prêt à être exécuté par le StatistiqueService.

    Raises:
        OutOfScopeError: Si aucun indicateur connu n'est détecté.
        AmbiguousQueryError: Si la question est ambiguë (ex. comparaison sans assez de régions).
    """
    norm_text = normalize_text(question)

    # 1. Indicateur (obligatoire)
    indicator = find_indicator(norm_text)
    if not indicator:
        # Vérification chit-chat avant OutOfScope
        chitchat_keywords = [
            "bonjour", "salut", "hello", "coucou", "comment ca va", 
            "comment vas tu", "comment vous allez", "ca va", "merci"
        ]
        if any(keyword in norm_text for keyword in chitchat_keywords):
            raise ChitChatError(
                "Bonjour ! Je vais très bien, merci. 😊 Je suis votre assistant "
                "statistique. Que souhaitez-vous analyser concernant les régions du Sénégal ?"
            )
            
        raise OutOfScopeError(
            "Désolé, je ne reconnais pas l'indicateur dans votre question. "
            "Je peux vous renseigner sur : la population, l'urbanisation, "
            "l'alphabétisation, le chômage, la pauvreté, l'accès internet, "
            "les centres de santé, la scolarisation et la production céréalière."
        )

    # 2. Régions
    regions = extract_regions(norm_text)

    # 3. Années
    start_year, end_year = extract_years(question)

    # 4. Opération
    operation = find_operation(norm_text)

    # 5. Règles de déduction automatique
    if len(regions) > 1 and operation == "value":
        operation = "compare"

    if start_year and end_year and start_year != end_year and operation == "value":
        operation = "trend"

    # 6. Détection d'ambiguïté
    if operation == "compare" and len(regions) < 2:
        raise AmbiguousQueryError(
            "Vous souhaitez comparer, mais vous n'avez mentionné qu'une seule région "
            "(ou aucune). Pourriez-vous préciser les régions à comparer ?"
        )

    # Extraction de la limite (top N) — force l'opération ranking
    limit = extract_limit(question)
    if limit is not None:
        operation = "ranking"

    # Type de graphique adapté à l'opération
    if operation == "trend":
        chart_type = "line"
    elif operation == "proportion":
        chart_type = "doughnut"  # Version plus esthétique du camembert
    else:
        chart_type = "bar"

    return QueryIntent(
        indicator=indicator,
        regions=regions,
        start_year=start_year,
        end_year=end_year,
        operation=operation,
        limit=limit,
        chart_type=chart_type,
    )
