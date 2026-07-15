from typing import List, Dict, Any, Optional
from django.db.models import Sum, Avg
from .models import StatistiqueRegionale
from apps.chatbot.dto import QueryIntent

class StatistiqueService:
    """
    Service gérant toute l'interaction avec la base de données.
    Implémente les 6 opérations métier et garantit la sécurité via une liste blanche.
    """
    
    # Règle de sécurité non négociable : Whitelist stricte des champs autorisés
    ALLOWED_INDICATORS = {
        "population", 
        "taux_urbanisation_pct", 
        "taux_alphabetisation_pct", 
        "taux_chomage_pct", 
        "taux_pauvrete_pct", 
        "acces_internet_pct", 
        "centres_sante", 
        "taux_scolarisation_pct", 
        "production_cerealiere_tonnes"
    }

    @classmethod
    def _validate_indicator(cls, indicator: str) -> str:
        """
        Garantit que le nom du champ passé à l'ORM provient bien de la liste blanche.
        """
        if not indicator or indicator not in cls.ALLOWED_INDICATORS:
            raise ValueError("Indicateur non autorisé ou manquant.")
        return indicator

    @classmethod
    def execute_query(cls, intent: QueryIntent) -> Dict[str, Any]:
        """
        Orchestre l'exécution de la requête selon l'opération demandée.
        Retourne un dictionnaire contenant les données formatées pour le tableau ('table')
        et la valeur agrégée si nécessaire ('answer_value').
        """
        indicator = cls._validate_indicator(intent.indicator)
        
        # Filtrage de base (années)
        qs = StatistiqueRegionale.objects.all()
        if intent.start_year and intent.end_year:
            qs = qs.filter(annee__gte=intent.start_year, annee__lte=intent.end_year)
        elif intent.start_year:
            qs = qs.filter(annee=intent.start_year)
            
        # Filtrage de base (régions) si spécifiées et si ce n'est pas un classement global
        if intent.regions and intent.operation != "ranking":
            qs = qs.filter(region__in=intent.regions)
            
        # Aiguillage selon l'opération
        if intent.operation == "value":
            return cls._handle_value(qs, indicator)
        elif intent.operation == "compare":
            return cls._handle_compare(qs, indicator)
        elif intent.operation == "trend":
            return cls._handle_trend(qs, indicator)
        elif intent.operation == "ranking":
            return cls._handle_ranking(qs, indicator, intent.regions, intent.limit)
        elif intent.operation == "sum":
            return cls._handle_aggregation(qs, indicator, Sum)
        elif intent.operation == "average":
            return cls._handle_aggregation(qs, indicator, Avg)
            
        raise ValueError(f"Opération non supportée : {intent.operation}")

    @classmethod
    def _handle_value(cls, qs, indicator: str) -> Dict[str, Any]:
        """Valeur simple."""
        qs = qs.order_by('-annee')
        table_data = list(qs.values('region', 'annee', indicator))
        val = table_data[0][indicator] if table_data else None
        return {"table": table_data, "answer_value": val}

    @classmethod
    def _handle_compare(cls, qs, indicator: str) -> Dict[str, Any]:
        """Comparaison de plusieurs régions."""
        qs = qs.order_by('-annee', f"-{indicator}")
        table_data = list(qs.values('region', 'annee', indicator))
        return {"table": table_data, "answer_value": None}

    @classmethod
    def _handle_trend(cls, qs, indicator: str) -> Dict[str, Any]:
        """Évolution temporelle d'une région."""
        qs = qs.order_by('annee')
        table_data = list(qs.values('region', 'annee', indicator))
        return {"table": table_data, "answer_value": None}

    @classmethod
    def _handle_ranking(cls, qs, indicator: str, limit_regions: List[str], limit: Optional[int]) -> Dict[str, Any]:
        """
        Classement (Top N).
        Si des régions sont spécifiées, on filtre d'abord dessus.
        """
        # On trie simplement par année desc puis valeur desc.
        qs = qs.order_by('-annee', f"-{indicator}")
        
        if limit_regions:
            qs = qs.filter(region__in=limit_regions)
            
        # Pour ne classer que sur une seule année (la plus récente du queryset)
        if qs.exists():
            year_to_rank = qs.first().annee
            qs = qs.filter(annee=year_to_rank)
            
        table_data = list(qs.values('region', 'annee', indicator))
        
        if limit:
            table_data = table_data[:limit]
            
        return {"table": table_data, "answer_value": None}

    @classmethod
    def _handle_aggregation(cls, qs, indicator: str, agg_func) -> Dict[str, Any]:
        """Somme ou Moyenne."""
        result = qs.aggregate(agg_value=agg_func(indicator))
        val = result['agg_value']
        
        # On retourne aussi les lignes qui ont servi au calcul pour la transparence (tableau)
        table_data = list(qs.order_by('-annee', 'region').values('region', 'annee', indicator))
        
        return {"table": table_data, "answer_value": val}
