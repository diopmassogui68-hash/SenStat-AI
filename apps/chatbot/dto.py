from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class QueryIntent:
    indicator: str
    regions: List[str] = field(default_factory=list)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    operation: str = "value"
    limit: Optional[int] = None
    chart_type: str = "bar"
