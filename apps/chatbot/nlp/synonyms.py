import unicodedata

def normalize_text(text: str) -> str:
    """Met le texte en minuscule et retire les accents."""
    text = str(text).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

INDICATOR_SYNONYMS = {
    "population": ["population", "habitants", "demographie", "monde", "personnes"],
    "taux_urbanisation_pct": ["urbanisation", "ville", "citadins", "taux d'urbanisation"],
    "taux_alphabetisation_pct": ["alphabetisation", "lettres", "lire et ecrire", "taux d'alphabetisation", "education"],
    "taux_chomage_pct": ["chomage", "sans emploi", "taux de chomage", "chomeurs"],
    "taux_pauvrete_pct": ["pauvrete", "pauvres", "taux de pauvrete", "precarite"],
    "acces_internet_pct": ["internet", "connexion", "web", "acces internet", "en ligne"],
    "centres_sante": ["sante", "hopitaux", "cliniques", "centres de sante", "dispensaires"],
    "taux_scolarisation_pct": ["scolarisation", "ecole", "eleves", "taux de scolarisation"],
    "production_cerealiere_tonnes": ["cereales", "agriculture", "recoltes", "production cerealiere", "tonnes de cereales"],
}

OPERATION_SYNONYMS = {
    "trend": ["evolution", "tendance", "historique", "au fil du temps", "depuis", "annees"],
    "compare": ["comparer", "compare", "difference", "contre", "vs", "versus"],
    "ranking": ["classement", "top", "meilleurs", "pires", "plus grand", "plus petit"],
    "sum": ["somme", "total", "cumul"],
    "average": ["moyenne", "en moyenne"],
    "value": ["valeur", "combien", "quel est", "quel etait", "quelle est"]
}

REGIONS_SENEGAL = [
    "Dakar", "Diourbel", "Fatick", "Kaffrine", "Kaolack", 
    "Kedougou", "Kolda", "Louga", "Matam", "Saint-Louis", 
    "Sedhiou", "Tambacounda", "Thies", "Ziguinchor"
]

def find_indicator(normalized_text: str) -> str | None:
    for indicator, synonyms in INDICATOR_SYNONYMS.items():
        for syn in synonyms:
            if normalize_text(syn) in normalized_text:
                return indicator
    return None

def find_operation(normalized_text: str) -> str:
    for operation, synonyms in OPERATION_SYNONYMS.items():
        for syn in synonyms:
            if normalize_text(syn) in normalized_text:
                return operation
    return "value"
