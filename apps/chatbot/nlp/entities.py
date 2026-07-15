import re
import unicodedata
from typing import List, Optional, Tuple
from .synonyms import INDICATORS_MAPPING, OPERATIONS_MAPPING, REGIONS_SENEGAL, OUT_OF_SCOPE_KEYWORDS

def normalize_text(text: str) -> str:
    """
    Supprime les accents, met en minuscule et retire la ponctuation.
    """
    if not text:
        return ""
    # Enlever les accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.lower()
    # Enlever ponctuation basique sauf traits d'union
    text = re.sub(r'[^\w\s-]', ' ', text)
    # Espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_regions(text: str) -> List[str]:
    """
    Extrait toutes les régions mentionnées dans le texte.
    Renvoie les noms des régions avec la casse d'origine correcte 
    pour la base de données.
    """
    normalized_text = normalize_text(text)
    found_regions = []
    
    # Mapping interne pour retrouver la bonne casse après normalisation
    region_proper_names = {
        "dakar": "Dakar", "diourbel": "Diourbel", "fatick": "Fatick", 
        "kaffrine": "Kaffrine", "kaolack": "Kaolack", "kedougou": "Kédougou", 
        "kolda": "Kolda", "louga": "Louga", "matam": "Matam", 
        "saint-louis": "Saint-Louis", "saint louis": "Saint-Louis", 
        "sedhiou": "Sédhiou", "tambacounda": "Tambacounda", 
        "thies": "Thiès", "ziguinchor": "Ziguinchor"
    }
    
    for region_lower in REGIONS_SENEGAL:
        # Regex pour matcher le mot exact (éviter que "dakar" matche dans "dakarois")
        pattern = r'\b' + re.escape(region_lower) + r'\b'
        if re.search(pattern, normalized_text):
            proper_name = region_proper_names[region_lower]
            if proper_name not in found_regions:
                found_regions.append(proper_name)
                
    return found_regions

def extract_years(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extrait les années mentionnées. Cherche des entiers entre 2020 et 2024.
    Retourne (start_year, end_year). S'il y a une seule année, start_year == end_year.
    """
    years = [int(y) for y in re.findall(r'\b202[0-4]\b', text)]
    
    if not years:
        return None, None
        
    years.sort()
    if len(years) == 1:
        return years[0], years[0]
    else:
        return years[0], years[-1]

def extract_indicator(text: str) -> Optional[str]:
    """
    Trouve l'indicateur demandé en cherchant les synonymes.
    Si plusieurs trouvés, on retourne le premier (géré comme ambiguïté plus tard si besoin).
    """
    normalized_text = normalize_text(text)
    
    # Chercher d'abord des mots multiples exacts si besoin, puis simples
    # Dans notre dictionnaire, les clés sont déjà en minuscules sans accent
    for synonym, column_name in INDICATORS_MAPPING.items():
        pattern = r'\b' + re.escape(synonym) + r'\b'
        if re.search(pattern, normalized_text):
            return column_name
            
    return None

def extract_operation(text: str, num_regions: int, num_years: int) -> str:
    """
    Déduit l'opération à effectuer.
    S'appuie d'abord sur les mots-clés, puis sur le contexte (nb régions/années).
    """
    normalized_text = normalize_text(text)
    
    # 1. Vérification par mots-clés explicites
    for synonym, op in OPERATIONS_MAPPING.items():
        pattern = r'\b' + re.escape(synonym) + r'\b'
        if re.search(pattern, normalized_text):
            return op
            
    # 2. Déduction contextuelle si pas de mot-clé
    if num_years > 1 and num_regions <= 1:
        return "trend"
    elif num_regions > 1:
        return "compare"
        
    # Par défaut
    return "value"

def detect_out_of_scope(text: str) -> bool:
    """
    Vérifie si la question contient des mots-clés totalement hors-sujet.
    """
    normalized_text = normalize_text(text)
    for word in OUT_OF_SCOPE_KEYWORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, normalized_text):
            return True
    return False

def extract_limit(text: str) -> Optional[int]:
    """
    Extrait une limite pour les requêtes de type 'top N'.
    Ex: "top 3", "5 meilleurs".
    """
    normalized_text = normalize_text(text)
    match = re.search(r'\b(?:top|les|des)\s+(\d+)\b', normalized_text)
    if match:
        limit = int(match.group(1))
        if 1 <= limit <= 14:  # Max 14 régions
            return limit
    
    # Si 'top' ou 'pire' est présent mais sans chiffre, on donne un default 3
    if re.search(r'\b(top|meilleurs|pires|premiers|derniers)\b', normalized_text):
        return 3
        
    return None
