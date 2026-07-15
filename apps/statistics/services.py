from typing import List, Dict, Any, Tuple
from django.db.models import Sum, Avg
from .models import StatistiqueRegionale
from apps.chatbot.dto import QueryIntent

WHITELIST_FIELDS = [
    'population', 'taux_urbanisation_pct', 'taux_alphabetisation_pct', 
    'taux_chomage_pct', 'taux_pauvrete_pct', 'acces_internet_pct', 
    'centres_sante', 'taux_scolarisation_pct', 'production_cerealiere_tonnes'
]

class StatistiqueService:
    @staticmethod
    def _validate_indicator(indicator: str) -> str:
        """Sécurité stricte : s'assure que le champ est dans la whitelist."""
        if indicator not in WHITELIST_FIELDS:
            raise ValueError(f"L'indicateur '{indicator}' n'est pas autorisé. Risque de sécurité bloqué.")
        return indicator

    @staticmethod
    def execute_query(intent: QueryIntent) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
        """Exécute la requête ORM de manière sécurisée et renvoie la réponse, les données et le graphique."""
        indicator = StatistiqueService._validate_indicator(intent.indicator)
        qs = StatistiqueRegionale.objects.all()

        if intent.regions:
            qs = qs.filter(region__in=intent.regions)
        
        if intent.start_year and intent.end_year:
            qs = qs.filter(annee__gte=intent.start_year, annee__lte=intent.end_year)
        elif intent.start_year:
            qs = qs.filter(annee=intent.start_year)

        table_data = []
        chart_data = None
        answer = ""

        if intent.operation == "value":
            data = list(qs.values('region', 'annee', indicator).order_by('region', 'annee'))
            table_data = data
            if data:
                val = data[0][indicator]
                answer = f"La valeur de '{indicator}' pour la région {data[0]['region']} en {data[0]['annee']} est de {val}."
            else:
                answer = "Aucune donnée trouvée pour cette requête."
            
            if data:
                chart_data = {
                    "type": intent.chart_type,
                    "labels": [f"{d['region']} ({d['annee']})" for d in data],
                    "datasets": [{"label": indicator, "data": [d[indicator] for d in data]}]
                }

        elif intent.operation == "compare":
            data = list(qs.values('region', 'annee', indicator).order_by('annee', 'region'))
            table_data = data
            if not data:
                answer = "Aucune donnée trouvée pour comparer."
            else:
                answer = f"Voici la comparaison pour '{indicator}'."
                labels = sorted(list(set(d['annee'] for d in data)))
                datasets = []
                regions_found = sorted(list(set(d['region'] for d in data)))
                for region in regions_found:
                    region_data = [next((item[indicator] for item in data if item['region'] == region and item['annee'] == y), 0) for y in labels]
                    datasets.append({"label": region, "data": region_data})
                
                chart_data = {
                    "type": intent.chart_type,
                    "labels": [str(l) for l in labels],
                    "datasets": datasets
                }

        elif intent.operation == "trend":
            data = list(qs.values('region', 'annee', indicator).order_by('annee'))
            table_data = data
            if not data:
                answer = "Aucune donnée trouvée pour l'évolution."
            else:
                answer = f"Voici l'évolution de '{indicator}' de {intent.start_year} à {intent.end_year}."
                labels = sorted(list(set(d['annee'] for d in data)))
                datasets = []
                regions_found = list(set(d['region'] for d in data))
                for region in regions_found:
                    region_data = [next((item[indicator] for item in data if item['region'] == region and item['annee'] == y), None) for y in labels]
                    datasets.append({"label": region, "data": region_data})

                chart_data = {
                    "type": intent.chart_type,
                    "labels": [str(l) for l in labels],
                    "datasets": datasets
                }

        elif intent.operation == "ranking":
            limit = intent.limit or 5
            # Si on demande un classement sans préciser d'année, on prend la plus récente disponible
            if not intent.start_year and not intent.end_year:
                qs = qs.filter(annee=2024)
                
            data = list(qs.values('region', 'annee', indicator).order_by(f'-{indicator}')[:limit])
            table_data = data
            if not data:
                answer = "Aucune donnée pour le classement."
            else:
                answer = f"Voici le top {limit} pour '{indicator}'."
                chart_data = {
                    "type": intent.chart_type,
                    "labels": [f"{d['region']} ({d['annee']})" for d in data],
                    "datasets": [{"label": indicator, "data": [d[indicator] for d in data]}]
                }

        elif intent.operation == "sum":
            result = qs.aggregate(total=Sum(indicator))
            total = result['total'] or 0
            table_data = [{"operation": "Somme", "indicateur": indicator, "valeur": total}]
            answer = f"La somme totale pour '{indicator}' est de {total}."
            chart_data = None

        elif intent.operation == "average":
            result = qs.aggregate(moyenne=Avg(indicator))
            moy = result['moyenne'] or 0
            moy = round(moy, 2)
            table_data = [{"operation": "Moyenne", "indicateur": indicator, "valeur": moy}]
            answer = f"La moyenne pour '{indicator}' est de {moy}."
            chart_data = None
            
        return answer, table_data, chart_data
