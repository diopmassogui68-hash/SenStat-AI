import os
import json
import logging
import google.generativeai as genai
from typing import Optional
from apps.chatbot.dto import QueryIntent

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client optionnel pour l'analyse NLP via l'API Gemini.
    Si cette classe échoue (timeout, clé absente, erreur de format), le système
    doit impérativement retomber sur l'analyseur déterministe (repli).
    """
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.is_configured = bool(self.api_key)
        if self.is_configured:
            genai.configure(api_key=self.api_key)
            # Utilisation de la configuration avec température basse pour une sortie déterministe
            self.generation_config = {
                "temperature": 0.1,
                "top_p": 1,
                "top_k": 1,
                "response_mime_type": "application/json",
            }
            # On utilise un modèle léger et rapide car c'est juste de l'extraction d'entités
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=self.generation_config
            )

    def analyze_intent(self, question: str) -> Optional[QueryIntent]:
        """
        Interroge Gemini pour parser la question et la structurer selon QueryIntent.
        Retourne None en cas de la moindre erreur.
        """
        if not self.is_configured:
            return None
            
        system_prompt = """
        Tu es un analyseur d'intention statistique pour les régions du Sénégal.
        Ta seule tâche est de lire la question de l'utilisateur et d'extraire les paramètres suivants au format JSON strict.
        
        Règles d'extraction :
        - indicator: Choisir STRICTEMENT parmi ["population", "taux_urbanisation_pct", "taux_alphabetisation_pct", "taux_chomage_pct", "taux_pauvrete_pct", "acces_internet_pct", "centres_sante", "taux_scolarisation_pct", "production_cerealiere_tonnes"]. Si aucun ne correspond, renvoie null.
        - regions: Liste de noms de régions (ex: ["Dakar", "Thiès"]).
        - start_year: entier (ex: 2020) ou null.
        - end_year: entier (ex: 2024) ou null.
        - operation: Choisir STRICTEMENT parmi ["value", "compare", "trend", "ranking", "sum", "average"].
        - limit: entier pour les classements (ex: 3 pour "top 3") ou null.
        
        Ne réponds RIEN D'AUTRE que le JSON brut.
        Format JSON attendu :
        {
          "indicator": "nom_exact",
          "regions": [],
          "start_year": 2020,
          "end_year": 2024,
          "operation": "value",
          "limit": null
        }
        """

        try:
            # Appel API avec timeout géré nativement (ou on assume un retour rapide du modèle flash)
            response = self.model.generate_content(f"{system_prompt}\n\nQuestion utilisateur: {question}")
            
            # Parsing du JSON
            data = json.loads(response.text)
            
            # Création de l'objet DTO
            intent = QueryIntent()
            intent.indicator = data.get('indicator')
            intent.regions = data.get('regions', [])
            intent.start_year = data.get('start_year')
            intent.end_year = data.get('end_year')
            intent.operation = data.get('operation', 'value')
            intent.limit = data.get('limit')
            
            # Délégation de l'ambiguïté et du chart_type à notre logique métier déterministe pour sécurité
            from apps.chatbot.nlp.intent_parser import IntentParser
            IntentParser._resolve_ambiguity(intent, question)
            IntentParser._determine_chart_type(intent)
            
            # Signalons dans l'objet qu'il a été généré par l'IA
            intent.is_ai_generated = True
            
            return intent
            
        except Exception as e:
            logger.warning(f"Échec de l'analyse Gemini, basculement vers le mode déterministe : {str(e)}")
            return None
