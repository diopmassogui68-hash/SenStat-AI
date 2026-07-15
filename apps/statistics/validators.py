"""
Validateurs métier pour l'import CSV des statistiques régionales.
Utilisés par la commande importer_statistiques et les tests.
"""

# --- Constantes de validation (pas de magic numbers) ---
ANNEE_MIN: int = 2020
ANNEE_MAX: int = 2024
POURCENTAGE_MIN: float = 0.0
POURCENTAGE_MAX: float = 100.0


def valider_annee(annee: int) -> bool:
    """Valide que l'année est comprise entre 2020 et 2024 inclus."""
    return ANNEE_MIN <= annee <= ANNEE_MAX


def valider_pourcentage(valeur: float) -> bool:
    """Valide qu'un pourcentage est compris entre 0 et 100 inclus."""
    return POURCENTAGE_MIN <= valeur <= POURCENTAGE_MAX


def nettoyer_region(region: str) -> str:
    """Nettoie le nom de la région : supprime les espaces superflus et normalise la casse.

    Gère correctement les noms composés avec trait d'union (ex. Saint-Louis).
    """
    region = region.strip()
    # .title() transforme "Saint-Louis" en "Saint-louis" → on corrige manuellement
    parts = region.split('-')
    return '-'.join(part.strip().capitalize() for part in parts)
