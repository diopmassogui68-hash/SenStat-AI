"""
Service métier pour les statistiques régionales.

Contient la whitelist de champs (sécurité) et l'exécution des 6 opérations ORM.
Aucune requête SQL n'est générée à partir du texte utilisateur.
"""
import logging
from typing import Any

from django.db.models import Sum, Avg

from .models import StatistiqueRegionale
from apps.chatbot.dto import QueryIntent

logger = logging.getLogger(__name__)

# --- SÉCURITÉ : liste blanche codée en dur (frozenset = immutable + lookup O(1)) ---
WHITELIST_FIELDS: frozenset[str] = frozenset({
    'population', 'taux_urbanisation_pct', 'taux_alphabetisation_pct',
    'taux_chomage_pct', 'taux_pauvrete_pct', 'acces_internet_pct',
    'centres_sante', 'taux_scolarisation_pct', 'production_cerealiere_tonnes',
})

# Noms lisibles en français pour les réponses textuelles (UX jury)
INDICATOR_LABELS: dict[str, str] = {
    'population': 'la population',
    'taux_urbanisation_pct': "le taux d'urbanisation",
    'taux_alphabetisation_pct': "le taux d'alphabétisation",
    'taux_chomage_pct': 'le taux de chômage',
    'taux_pauvrete_pct': 'le taux de pauvreté',
    'acces_internet_pct': "l'accès internet",
    'centres_sante': 'le nombre de centres de santé',
    'taux_scolarisation_pct': 'le taux de scolarisation',
    'production_cerealiere_tonnes': 'la production céréalière (tonnes)',
}


def _get_label(indicator: str) -> str:
    """Retourne le libellé français lisible d'un indicateur."""
    return INDICATOR_LABELS.get(indicator, indicator)


class StatistiqueService:
    """Service central pour l'exécution sécurisée des requêtes ORM.

    Toutes les opérations (value, compare, trend, ranking, sum, average)
    passent par la whitelist avant d'accéder à l'ORM.
    """

    @staticmethod
    def _validate_indicator(indicator: str) -> str:
        """Vérifie que l'indicateur est dans la whitelist. Lève ValueError sinon."""
        if indicator not in WHITELIST_FIELDS:
            raise ValueError(
                f"L'indicateur « {indicator} » n'est pas autorisé. "
                "Seuls les champs de la whitelist sont acceptés."
            )
        return indicator

    @staticmethod
    def execute_query(
        intent: QueryIntent,
    ) -> tuple[str, list[dict[str, Any]], dict[str, Any] | None]:
        """Exécute la requête ORM correspondant à l'intention et retourne (réponse, tableau, graphique).

        Args:
            intent: L'intention structurée issue du NLP ou de Gemini.

        Returns:
            Un tuple (answer, table_data, chart_data) conforme au contrat JSON de l'API.
        """
        indicator = StatistiqueService._validate_indicator(intent.indicator)
        label = _get_label(indicator)
        qs = StatistiqueRegionale.objects.all()

        # --- Filtrage par région et année ---
        if intent.regions:
            qs = qs.filter(region__in=intent.regions)

        if intent.start_year and intent.end_year:
            qs = qs.filter(annee__gte=intent.start_year, annee__lte=intent.end_year)
        elif intent.start_year:
            qs = qs.filter(annee=intent.start_year)

        table_data: list[dict[str, Any]] = []
        chart_data: dict[str, Any] | None = None
        answer: str = ""

        # --- Opération VALUE ---
        if intent.operation == "value":
            data = list(qs.values('region', 'annee', indicator).order_by('region', 'annee'))
            table_data = data
            if data:
                premier = data[0]
                answer = (
                    f"{_get_label(indicator).capitalize()} pour {premier['region']} "
                    f"en {premier['annee']} est de {premier[indicator]}."
                )
                chart_data = {
                    "type": intent.chart_type,
                    "labels": [f"{d['region']} ({d['annee']})" for d in data],
                    "datasets": [{"label": label, "data": [d[indicator] for d in data]}],
                }
            else:
                answer = "Aucune donnée trouvée pour cette requête."

        # --- Opération COMPARE ---
        elif intent.operation == "compare":
            data = list(qs.values('region', 'annee', indicator).order_by('annee', 'region'))
            table_data = data
            if not data:
                answer = "Aucune donnée trouvée pour cette comparaison."
            else:
                regions_txt = ", ".join(sorted(set(d['region'] for d in data)))
                answer = f"Comparaison de {label} entre {regions_txt}."
                labels = sorted(set(d['annee'] for d in data))
                regions_found = sorted(set(d['region'] for d in data))
                datasets = []
                for region in regions_found:
                    region_data = [
                        next(
                            (item[indicator] for item in data
                             if item['region'] == region and item['annee'] == y),
                            0,
                        )
                        for y in labels
                    ]
                    datasets.append({"label": region, "data": region_data})

                chart_data = {
                    "type": intent.chart_type,
                    "labels": [str(y) for y in labels],
                    "datasets": datasets,
                }

        # --- Opération TREND ---
        elif intent.operation == "trend":
            data = list(qs.values('region', 'annee', indicator).order_by('annee'))
            table_data = data
            if not data:
                answer = "Aucune donnée trouvée pour l'évolution demandée."
            else:
                answer = (
                    f"Évolution de {label} de {intent.start_year} à {intent.end_year}."
                )
                labels = sorted(set(d['annee'] for d in data))
                regions_found = sorted(set(d['region'] for d in data))
                datasets = []
                for region in regions_found:
                    region_data = [
                        next(
                            (item[indicator] for item in data
                             if item['region'] == region and item['annee'] == y),
                            None,
                        )
                        for y in labels
                    ]
                    datasets.append({"label": region, "data": region_data})

                chart_data = {
                    "type": intent.chart_type,
                    "labels": [str(y) for y in labels],
                    "datasets": datasets,
                }

        # --- Opération RANKING ---
        elif intent.operation == "ranking":
            limit = intent.limit or 5
            if not intent.start_year and not intent.end_year:
                qs = qs.filter(annee=2024)

            data = list(
                qs.values('region', 'annee', indicator)
                .order_by(f'-{indicator}')[:limit]
            )
            table_data = data
            if not data:
                answer = "Aucune donnée disponible pour ce classement."
            else:
                answer = f"Top {limit} pour {label}."
                chart_data = {
                    "type": intent.chart_type,
                    "labels": [d['region'] for d in data],
                    "datasets": [{"label": label, "data": [d[indicator] for d in data]}],
                }

        # --- Opération SUM ---
        elif intent.operation == "sum":
            result = qs.aggregate(total=Sum(indicator))
            total = result['total'] or 0
            total = round(total, 2)
            table_data = [{"opération": "Somme", "indicateur": label, "valeur": total}]
            answer = f"La somme totale de {label} est de {total}."

        # --- Opération AVERAGE ---
        elif intent.operation == "average":
            result = qs.aggregate(moyenne=Avg(indicator))
            moy = round(result['moyenne'] or 0, 2)
            table_data = [{"opération": "Moyenne", "indicateur": label, "valeur": moy}]
            answer = f"La moyenne de {label} est de {moy}."

        return answer, table_data, chart_data
