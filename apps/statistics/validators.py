def valider_annee(annee: int) -> bool:
    """Valide que l'année est comprise entre 2020 et 2024."""
    return 2020 <= annee <= 2024

def valider_pourcentage(valeur: float) -> bool:
    """Valide qu'un pourcentage est compris entre 0 et 100."""
    return 0.0 <= valeur <= 100.0

def nettoyer_region(region: str) -> str:
    """Nettoie le nom de la région (espaces, casse)."""
    return region.strip().title()
