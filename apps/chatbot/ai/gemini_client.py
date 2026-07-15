"""
Client Gemini (bonus optionnel) — appel API sans librairie externe.

Utilise urllib.request (stdlib) pour appeler l'API Gemini et
extraire un QueryIntent structuré. En cas d'échec, timeout ou
réponse invalide, retourne None pour basculer silencieusement
sur le parseur NLP déterministe.

Règle de sécurité : l'indicateur retourné par Gemini est TOUJOURS
validé contre la whitelist avant d'être utilisé.
"""
import json
import logging
import os
import urllib.request
from typing import Optional

from apps.chatbot.dto import QueryIntent
from apps.statistics.services import WHITELIST_FIELDS

logger = logging.getLogger(__name__)

# Timeout en secondes pour l'appel API (suffisamment court pour un repli rapide)
GEMINI_TIMEOUT: int = 5


def _build_prompt(question: str) -> str:
    """Construit le prompt système pour Gemini avec le schéma JSON strict."""
    return (
        "Tu es un assistant d'analyse de données statistiques régionales au Sénégal. "
        "Transforme la question utilisateur en objet JSON strict, sans aucun autre texte.\n\n"
        "Indicateurs autorisés : population, taux_urbanisation_pct, "
        "taux_alphabetisation_pct, taux_chomage_pct, taux_pauvrete_pct, "
        "acces_internet_pct, centres_sante, taux_scolarisation_pct, "
        "production_cerealiere_tonnes.\n"
        "Opérations : value, compare, trend, ranking, sum, average.\n"
        "Régions : Dakar, Diourbel, Fatick, Kaffrine, Kaolack, Kedougou, "
        "Kolda, Louga, Matam, Saint-Louis, Sedhiou, Tambacounda, Thies, Ziguinchor.\n"
        "Années : 2020 à 2024 uniquement.\n\n"
        "Schéma de sortie :\n"
        '{"indicator": "...", "regions": [...], "start_year": ..., '
        '"end_year": ..., "operation": "...", "limit": null, "chart_type": "bar"}\n\n'
        f'Question : "{question}"'
    )


def call_gemini(question: str) -> Optional[QueryIntent]:
    """Appelle l'API Gemini pour extraire l'intention structurée.

    Args:
        question: La question brute de l'utilisateur.

    Returns:
        Un QueryIntent validé, ou None si l'appel échoue ou si la réponse
        est invalide (déclenchant le repli vers le NLP déterministe).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )

    payload = {
        "contents": [{"parts": [{"text": _build_prompt(question)}]}],
        "generationConfig": {
            "temperature": 0.0,
            "response_mime_type": "application/json",
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )

    try:
        with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as response:
            result = json.loads(response.read().decode())
            text = result['candidates'][0]['content']['parts'][0]['text']
            parsed = json.loads(text)

            # Validation stricte de l'indicateur contre la whitelist
            indicator = parsed.get("indicator")
            if not indicator or indicator not in WHITELIST_FIELDS:
                logger.warning(
                    "Gemini a retourné un indicateur invalide : %s", indicator
                )
                return None

            return QueryIntent(
                indicator=indicator,
                regions=parsed.get("regions", []),
                start_year=parsed.get("start_year"),
                end_year=parsed.get("end_year"),
                operation=parsed.get("operation", "value"),
                limit=parsed.get("limit"),
                chart_type=parsed.get("chart_type", "bar"),
            )

    except Exception as e:
        logger.warning(
            "Échec Gemini : %s — basculement silencieux sur le NLP déterministe.", e
        )
        return None
