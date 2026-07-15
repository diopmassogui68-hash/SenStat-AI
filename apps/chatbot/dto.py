from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class QueryIntent:
    """
    Objet de Transfert de Données (DTO) représentant l'intention extraite de la question utilisateur.
    """
    indicator: Optional[str] = None
    regions: List[str] = field(default_factory=list)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    operation: str = "value"  # value, compare, trend, ranking, sum, average
    limit: Optional[int] = None
    chart_type: Optional[str] = None
    is_ambiguous: bool = False
    ambiguity_reason: Optional[str] = None
    is_out_of_scope: bool = False
    is_ai_generated: bool = False
    
    def to_dict(self):
        return {
            "indicator": self.indicator,
            "regions": self.regions,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "operation": self.operation,
            "limit": self.limit,
            "chart_type": self.chart_type
        }
