import re
from typing import List, Tuple
from .synonyms import normalize_text, REGIONS_SENEGAL

def extract_years(text: str) -> Tuple[int | None, int | None]:
    """Extrait une année simple ou une plage d'années (ex: 2020-2022, entre 2021 et 2023)."""
    matches = re.findall(r'\b(202[0-4])\b', text)
    if not matches:
        return None, None
    years = sorted([int(y) for y in matches])
    if len(years) == 1:
        # Check if "depuis"
        if "depuis" in normalize_text(text):
            return years[0], 2024
        return years[0], years[0]
    return years[0], years[-1]

def extract_regions(normalized_text: str) -> List[str]:
    """Extrait toutes les régions mentionnées dans le texte."""
    found_regions = []
    for region in REGIONS_SENEGAL:
        if normalize_text(region) in normalized_text:
            found_regions.append(region)
    return found_regions

def extract_limit(text: str) -> int | None:
    """Extrait la limite pour les classements (ex: top 3)."""
    match = re.search(r'\btop\s*(\d+)\b', normalize_text(text))
    if match:
        return int(match.group(1))
    return None
