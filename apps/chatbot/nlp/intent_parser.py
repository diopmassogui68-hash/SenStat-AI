import re
import json
import logging
import warnings
from django.conf import settings

# Ignorer le futur warning de deprecation de google.generativeai
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    import google.generativeai as genai

logger = logging.getLogger(__name__)

class QueryIntent:
    def __init__(self, operation="value", indicator="inconnu", regions=None, start_year=None, end_year=None):
        self.operation = operation
        self.indicator = indicator
        self.regions = regions or []
        self.start_year = start_year
        self.end_year = end_year

    def to_dict(self):
        return {
            "operation": self.operation,
            "indicator": self.indicator,
            "regions": self.regions,
            "start_year": self.start_year,
            "end_year": self.end_year
        }

class IntentParser:
    INDICATORS_MAPPING = {
        "population": "population",
        "habitant": "population",
        "urbanisation": "taux_urbanisation_pct",
        "ville": "taux_urbanisation_pct",
        "alphabétisation": "taux_alphabetisation_pct",
        "alphabetisation": "taux_alphabetisation_pct",
        "chômage": "taux_chomage_pct",
        "chomage": "taux_chomage_pct",
        "travail": "taux_chomage_pct",
        "pauvreté": "taux_pauvrete_pct",
        "pauvrete": "taux_pauvrete_pct",
        "internet": "acces_internet_pct",
        "connexion": "acces_internet_pct",
        "santé": "centres_sante",
        "sante": "centres_sante",
        "hôpitaux": "centres_sante",
        "hopitaux": "centres_sante",
        "scolarisation": "taux_scolarisation_pct",
        "école": "taux_scolarisation_pct",
        "ecole": "taux_scolarisation_pct",
        "céréale": "production_cerealiere_tonnes",
        "cereale": "production_cerealiere_tonnes",
        "production": "production_cerealiere_tonnes",
        "agriculture": "production_cerealiere_tonnes"
    }

    REGIONS = [
        "Dakar", "Thiès", "Thies", "Diourbel", "Louga", "Saint-Louis", "Fatick", 
        "Kaolack", "Kaffrine", "Tambacounda", "Kédougou", "Kedougou", "Kolda", 
        "Sédhiou", "Sedhiou", "Ziguinchor", "Matam"
    ]

    def __init__(self):
        # Configure Gemini if API key is present
        self.use_gemini = False
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_gemini = True
            logger.info("Gemini AI est configuré pour le parsing d'intention.")

    def parse(self, text: str) -> QueryIntent:
        intent = None
        if self.use_gemini:
            try:
                intent = self._parse_with_llm(text)
            except Exception as e:
                logger.error(f"Erreur lors de l'utilisation de Gemini : {e}. Repli déterministe.")
        
        if not intent:
            intent = self._parse_deterministic(text)
        
        return intent

    def _parse_with_llm(self, text: str) -> QueryIntent:
        prompt = f"""
        Tu es un analyseur d'intention pour une base de données statistiques régionales du Sénégal.
        Extrais les informations de la question suivante et renvoie UNIQUEMENT un JSON valide avec ces clés :
        - operation : "value" (pour une valeur simple), "compare" (pour comparer des régions), "trend" (pour une évolution dans le temps), ou "average" (pour une moyenne).
        - indicator : doit être parmi ["population", "taux_urbanisation_pct", "taux_alphabetisation_pct", "taux_chomage_pct", "taux_pauvrete_pct", "acces_internet_pct", "centres_sante", "taux_scolarisation_pct", "production_cerealiere_tonnes"].
        - regions : liste des régions mentionnées. Ex: ["Dakar", "Thiès"].
        - start_year : année de début (ex: 2020), ou null.
        - end_year : année de fin (ex: 2024), ou null.

        Question : "{text}"
        """
        response = self.model.generate_content(prompt)
        content = response.text.strip()
        
        # Nettoyer si le modèle ajoute des backticks
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content)
        return QueryIntent(
            operation=data.get("operation", "value"),
            indicator=data.get("indicator", "inconnu"),
            regions=data.get("regions", []),
            start_year=data.get("start_year"),
            end_year=data.get("end_year")
        )

    def _parse_deterministic(self, text: str) -> QueryIntent:
        text_lower = text.lower()
        intent = QueryIntent()

        # 1. Operation
        if "top" in text_lower or "classement" in text_lower or "meilleur" in text_lower or "pire" in text_lower:
            intent.operation = "top"
        elif "compar" in text_lower or "différence" in text_lower or "vs" in text_lower:
            intent.operation = "compare"
        elif "évolution" in text_lower or "evolution" in text_lower or "tendance" in text_lower:
            intent.operation = "trend"
        elif "moyenne" in text_lower:
            intent.operation = "average"
        else:
            intent.operation = "value"

        # 2. Indicator
        for keyword, field in self.INDICATORS_MAPPING.items():
            if keyword in text_lower:
                intent.indicator = field
                break

        # 3. Regions
        regions_found = []
        for r in self.REGIONS:
            # Remplacement basique des accents pour la comparaison
            r_normalized = r.lower().replace("è", "e").replace("é", "e")
            t_normalized = text_lower.replace("è", "e").replace("é", "e")
            
            # Match strict de mot
            pattern = r'\b' + re.escape(r_normalized) + r'\b'
            if re.search(pattern, t_normalized):
                # Utiliser le nom officiel avec la bonne casse (premier match)
                official_region = r.replace("Thies", "Thiès").replace("Kedougou", "Kédougou").replace("Sedhiou", "Sédhiou")
                if official_region not in regions_found:
                    regions_found.append(official_region)
        intent.regions = regions_found

        # 4. Years
        years = re.findall(r'\b(20[2-9][0-9])\b', text)
        if years:
            years = sorted([int(y) for y in set(years)])
            intent.start_year = years[0]
            if len(years) > 1:
                intent.end_year = years[-1]
                if intent.operation == "value":
                    intent.operation = "trend" # Forcer trend s'il y a 2 dates

        return intent
