"""
Extracteurs d'entités pour le moteur NLP déterministe.

Extrait les régions, les années et les limites (top N) à partir
du texte brut de la question utilisateur.
"""
import re
from typing import Optional

from .synonyms import normalize_text, REGIONS_SENEGAL


def extract_years(text: str) -> tuple[Optional[int], Optional[int]]:
    """Extrait une année simple ou une plage d'années depuis le texte brut.

    Exemples reconnus :
      - "en 2022" → (2022, 2022)
      - "de 2020 à 2023" → (2020, 2023)
      - "depuis 2021" → (2021, 2024)
      - pas d'année → (None, None)

    Args:
        text: Texte brut de la question (non normalisé, pour conserver les chiffres).

    Returns:
        Tuple (start_year, end_year). Les deux sont None si aucune année détectée.
    """
    matches = re.findall(r'\b(202[0-4])\b', text)
    if not matches:
        return None, None

    years = sorted(int(y) for y in matches)

    if len(years) == 1:
        # "depuis 2021" → plage 2021-2024
        if "depuis" in normalize_text(text):
            return years[0], 2024
        return years[0], years[0]

    return years[0], years[-1]


def extract_regions(normalized_text: str) -> list[str]:
    """Extrait toutes les régions du Sénégal mentionnées dans le texte normalisé.

    La comparaison est insensible à la casse et aux accents.

    Args:
        normalized_text: Texte de la question, déjà normalisé.

    Returns:
        Liste des noms de régions trouvés (noms officiels avec casse correcte).
    """
    found_regions: list[str] = []
    for region in REGIONS_SENEGAL:
        if normalize_text(region) in normalized_text:
            found_regions.append(region)
    return found_regions


def extract_limit(text: str) -> Optional[int]:
    """Extrait la limite numérique pour les classements (ex. 'top 3', 'top 5').

    Args:
        text: Texte brut de la question.

    Returns:
        La limite entière, ou None si aucun motif 'top N' détecté.
    """
    match = re.search(r'\btop\s*(\d+)\b', normalize_text(text))
    if match:
        return int(match.group(1))
    return None
