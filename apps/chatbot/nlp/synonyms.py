"""
Dictionnaire de synonymes pour le moteur NLP déterministe.

Permet la reconnaissance des indicateurs, opérations et régions du Sénégal
de manière insensible à la casse et aux accents.

Note : les synonymes sont stockés SANS accents pour être comparés
au texte normalisé par normalize_text().
"""
import unicodedata
import difflib


def normalize_text(text: str) -> str:
    """Normalise le texte : minuscules, suppression des accents.

    Args:
        text: Texte brut à normaliser.

    Returns:
        Texte en minuscules sans accents.
    """
    text = str(text).lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


# --- Synonymes des indicateurs statistiques ---
# Clé = nom exact du champ Django, Valeurs = alias normalisés (sans accents)
# Les synonymes les plus longs sont placés EN PREMIER pour éviter les faux positifs
# (ex. "production cerealiere" doit être testé avant "production")
INDICATOR_SYNONYMS: dict[str, list[str]] = {
    "population": [
        "population", "habitants", "demographie", "nombre d'habitants",
    ],
    "taux_urbanisation_pct": [
        "taux d'urbanisation", "urbanisation", "taux urbanisation",
    ],
    "taux_alphabetisation_pct": [
        "taux d'alphabetisation", "alphabetisation", "lire et ecrire",
    ],
    "taux_chomage_pct": [
        "taux de chomage", "chomage", "sans emploi", "chomeurs",
    ],
    "taux_pauvrete_pct": [
        "taux de pauvrete", "pauvrete", "pauvres", "precarite",
    ],
    "acces_internet_pct": [
        "acces internet", "acces a internet", "internet", "connexion internet",
    ],
    "centres_sante": [
        "centres de sante", "centre de sante", "hopitaux", "cliniques", "dispensaires",
    ],
    "taux_scolarisation_pct": [
        "taux de scolarisation", "scolarisation", "scolarise",
    ],
    "production_cerealiere_tonnes": [
        "production cerealiere", "cereales", "recoltes cerealiere",
        "tonnes de cereales",
    ],
}

# --- Synonymes des opérations ---
# L'ordre du dictionnaire définit la priorité de détection.
# Les opérations spécifiques (ranking, sum, average) sont testées AVANT value
# pour éviter qu'un mot générique ne les masque.
OPERATION_SYNONYMS: dict[str, list[str]] = {
    "trend": [
        "evolution", "tendance", "historique", "au fil du temps",
        "progresse", "evolue",
    ],
    "compare": [
        "comparer", "compare", "comparaison", "difference",
        "contre", "vs", "versus",
    ],
    "ranking": [
        "classement", "top", "meilleurs", "pires",
        "plus eleve", "plus faible",
    ],
    "sum": ["somme", "cumul"],
    "average": ["moyenne", "en moyenne"],
    "proportion": ["proportion", "repartition", "part ", "parts"],
    "value": ["valeur", "combien", "quel est", "quelle est"],
}

# --- Les 14 régions officielles du Sénégal ---
REGIONS_SENEGAL: list[str] = [
    "Dakar", "Diourbel", "Fatick", "Kaffrine", "Kaolack",
    "Kédougou", "Kolda", "Louga", "Matam", "Saint-Louis",
    "Sédhiou", "Tambacounda", "Thiès", "Ziguinchor",
]


def find_indicator(normalized_text: str) -> str | None:
    """Recherche l'indicateur statistique dans le texte normalisé.

    Les synonymes longs sont testés en premier pour éviter les faux positifs.

    Args:
        normalized_text: Texte de la question, déjà normalisé (sans accents, minuscules).

    Returns:
        Le nom du champ Django correspondant, ou None si aucun indicateur détecté.
    """
    # 1. Correspondance exacte
    for indicator, synonyms in INDICATOR_SYNONYMS.items():
        for syn in synonyms:
            if syn in normalized_text:
                return indicator
                
    # 2. Correspondance floue par mot (tolérance aux fautes d'orthographe)
    words = normalized_text.split()
    for word in words:
        if len(word) >= 5:  # Seulement les mots significatifs
            for indicator, synonyms in INDICATOR_SYNONYMS.items():
                for syn in synonyms:
                    for syn_word in syn.split():
                        if len(syn_word) >= 5:
                            # Calcul de similarité
                            ratio = difflib.SequenceMatcher(None, word, syn_word).ratio()
                            if ratio > 0.8:
                                return indicator
                                
    return None


def find_operation(normalized_text: str) -> str:
    """Détecte l'opération demandée dans le texte normalisé.

    Retourne 'value' par défaut si aucune opération spécifique n'est détectée.

    Args:
        normalized_text: Texte de la question, déjà normalisé.

    Returns:
        Le code de l'opération (value, compare, trend, ranking, sum, average).
    """
    # 1. Correspondance exacte
    for operation, synonyms in OPERATION_SYNONYMS.items():
        for syn in synonyms:
            if syn in normalized_text:
                return operation
                
    # 2. Correspondance floue
    words = normalized_text.split()
    for word in words:
        if len(word) >= 5:
            for operation, synonyms in OPERATION_SYNONYMS.items():
                for syn in synonyms:
                    for syn_word in syn.split():
                        if len(syn_word) >= 5:
                            ratio = difflib.SequenceMatcher(None, word, syn_word).ratio()
                            if ratio > 0.8:
                                return operation
                                
    return "value"
