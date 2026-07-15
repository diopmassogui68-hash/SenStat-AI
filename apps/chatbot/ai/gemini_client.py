import os
import json
import logging
import urllib.request
from apps.chatbot.dto import QueryIntent

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# On utilise le format v1beta pour bénéficier de response_mime_type=application/json
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

def call_gemini(question: str) -> QueryIntent | None:
    """Appelle Gemini API pour extraire l'intention structurée, retourne None en cas d'échec (pour activer le repli)."""
    if not GEMINI_API_KEY:
        return None

    prompt = f"""
    Tu es un assistant d'analyse de données statistiques régionales au Sénégal.
    Ta tâche est de transformer la question utilisateur en objet JSON strict sans aucun autre texte.
    Les indicateurs autorisés sont : population, taux_urbanisation_pct, taux_alphabetisation_pct, taux_chomage_pct, taux_pauvrete_pct, acces_internet_pct, centres_sante, taux_scolarisation_pct, production_cerealiere_tonnes.
    Les opérations sont : value, compare, trend, ranking, sum, average.
    
    Exemple de sortie attendue :
    {{
      "indicator": "acces_internet_pct",
      "regions": ["Kaolack"],
      "start_year": 2020,
      "end_year": 2024,
      "operation": "trend",
      "limit": null,
      "chart_type": "line"
    }}
    
    Question utilisateur : "{question}"
    """
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "response_mime_type": "application/json",
        }
    }
    
    req = urllib.request.Request(
        GEMINI_URL, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # Timeout très court (3s) pour assurer le repli rapide vers le mode déterministe
        with urllib.request.urlopen(req, timeout=3) as response:
            result = json.loads(response.read().decode())
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            parsed = json.loads(text)
            # Validation de l'indicateur basique avant de retourner l'objet
            indicator = parsed.get("indicator")
            if not indicator:
                return None
                
            return QueryIntent(
                indicator=indicator,
                regions=parsed.get("regions", []),
                start_year=parsed.get("start_year"),
                end_year=parsed.get("end_year"),
                operation=parsed.get("operation", "value"),
                limit=parsed.get("limit"),
                chart_type=parsed.get("chart_type", "bar")
            )
            
    except Exception as e:
        logger.warning(f"Échec Gemini (timeout ou erreur) : {str(e)}. Basculement silencieux sur NLP local.")
        return None
