"""
DTO (Data Transfer Object) pour structurer l'intention extraite d'une question utilisateur.

Ce dataclass est le contrat interne entre le NLP/Gemini et le moteur ORM.
Il ne contient jamais de SQL ni de nom de champ non validé.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryIntent:
    """Intention structurée issue de l'analyse d'une question en langage naturel.

    Attributes:
        indicator: Nom du champ statistique (doit être dans la whitelist).
        regions: Liste des régions mentionnées (vide = toutes).
        start_year: Année de début (None = pas de filtre temporel).
        end_year: Année de fin (None = pas de filtre temporel).
        operation: Type d'opération (value, compare, trend, ranking, sum, average).
        limit: Nombre max de résultats pour les classements (None = pas de limite).
        chart_type: Type de graphique suggéré pour Chart.js (bar, line).
    """

    indicator: str
    regions: list[str] = field(default_factory=list)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    operation: str = "value"
    limit: Optional[int] = None
    chart_type: str = "bar"
