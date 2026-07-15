"""
Dictionnaires de synonymes pour le traitement du langage naturel (NLP).
Fait la correspondance entre les mots de l'utilisateur et les champs internes.
"""

# Mapping des indicateurs (mots-clés vers noms de colonnes exacts)
INDICATORS_MAPPING = {
    # Population
    "population": "population",
    "habitants": "population",
    "demographie": "population",
    "nombre de personnes": "population",
    
    # Urbanisation
    "urbanisation": "taux_urbanisation_pct",
    "urbain": "taux_urbanisation_pct",
    "ville": "taux_urbanisation_pct",
    
    # Alphabétisation
    "alphabetisation": "taux_alphabetisation_pct",
    "alphabetises": "taux_alphabetisation_pct",
    "lettres": "taux_alphabetisation_pct",
    
    # Chômage
    "chomage": "taux_chomage_pct",
    "chomeurs": "taux_chomage_pct",
    "sans emploi": "taux_chomage_pct",
    
    # Pauvreté
    "pauvrete": "taux_pauvrete_pct",
    "pauvres": "taux_pauvrete_pct",
    
    # Accès internet
    "internet": "acces_internet_pct",
    "connectivite": "acces_internet_pct",
    "connexion": "acces_internet_pct",
    "en ligne": "acces_internet_pct",
    
    # Santé
    "sante": "centres_sante",
    "hopitaux": "centres_sante",
    "cliniques": "centres_sante",
    "dispensaires": "centres_sante",
    "structures sanitaires": "centres_sante",
    
    # Scolarisation
    "scolarisation": "taux_scolarisation_pct",
    "ecole": "taux_scolarisation_pct",
    "eleves": "taux_scolarisation_pct",
    
    # Production céréalière
    "cereales": "production_cerealiere_tonnes",
    "production": "production_cerealiere_tonnes",
    "agriculture": "production_cerealiere_tonnes",
    "recolte": "production_cerealiere_tonnes"
}

# Mapping des opérations
OPERATIONS_MAPPING = {
    # Compare
    "comparer": "compare",
    "difference": "compare",
    "par rapport": "compare",
    "versus": "compare",
    "vs": "compare",
    
    # Trend
    "evolution": "trend",
    "tendance": "trend",
    "progression": "trend",
    "historique": "trend",
    "depuis": "trend",
    "entre": "trend",
    
    # Ranking
    "top": "ranking",
    "meilleurs": "ranking",
    "pires": "ranking",
    "classement": "ranking",
    "plus": "ranking",
    "moins": "ranking",
    "premier": "ranking",
    "dernier": "ranking",
    
    # Sum
    "total": "sum",
    "somme": "sum",
    "cumul": "sum",
    "global": "sum",
    
    # Average
    "moyenne": "average",
    "en moyenne": "average"
}

# Liste des 14 régions du Sénégal (en minuscule, sans accent pour la comparaison)
REGIONS_SENEGAL = [
    "dakar", "diourbel", "fatick", "kaffrine", "kaolack", 
    "kedougou", "kolda", "louga", "matam", "saint-louis", 
    "saint louis", "sedhiou", "tambacounda", "thies", "ziguinchor"
]

# Liste des mots hors sujet (pour refus poli)
OUT_OF_SCOPE_KEYWORDS = [
    "meteo", "president", "politique", "sport", "football", 
    "musique", "recette", "cinema"
]
