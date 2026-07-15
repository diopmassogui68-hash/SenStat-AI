from apps.chatbot.nlp.intent_parser import IntentParser
from apps.chatbot.repositories.statistique_repository import StatistiqueRepository

class QuestionService:
    def __init__(self):
        self.parser = IntentParser()
        self.repository = StatistiqueRepository()

    def process_question(self, text: str) -> dict:
        # 1. Parse l'intention
        intent = self.parser.parse(text)
        
        # 2. Récupère les données
        data, rows_used = self.repository.execute_query(intent)
        
        # 3. Construit la réponse texte
        answer = self._generate_answer(intent, data)
        
        # 4. Construit le format pour Chart.js
        chart_config = self._generate_chart_config(intent, data)

        # 5. Formate les données pour le tableau
        table_data = self._format_table_data(data)
        
        return {
            "answer": answer,
            "table": table_data,
            "chart": chart_config,
            "metadata": {"rows_used": rows_used, "fictitious": True},
            "intent": intent.to_dict()
        }

    def _generate_answer(self, intent, data) -> str:
        if not data:
            return "Je suis désolé, je n'ai trouvé aucune donnée correspondant à votre demande."
        
        # Génération basique selon l'opération
        if intent.operation == "value":
            if len(data) == 1:
                item = data[0]
                val = item.get(intent.indicator)
                return f"Voici la valeur pour {item.get('region', 'la région')} en {item['annee']} : {val}."
            return f"J'ai trouvé {len(data)} valeurs pour votre recherche concernant l'indicateur {intent.indicator}."
            
        elif intent.operation == "compare":
            return f"Voici la comparaison de l'indicateur {intent.indicator} pour les régions sélectionnées."
            
        elif intent.operation == "top":
            return f"Voici le classement (Top) pour l'indicateur {intent.indicator}."
            
        elif intent.operation == "trend":
            return f"Voici l'évolution de l'indicateur {intent.indicator} sur la période demandée."
            
        elif intent.operation == "average":
            return f"Voici la moyenne de l'indicateur {intent.indicator}."
            
        return "Voici les résultats de votre recherche."

    def _generate_chart_config(self, intent, data) -> dict:
        if not data or len(data) < 2:
            return None # Pas de graphique pour une seule valeur

        chart = {"type": "bar", "labels": [], "datasets": []}
        
        # Palette de couleurs stylisée
        colors = [
            "rgba(13, 110, 253, 0.7)", # Blue
            "rgba(25, 135, 84, 0.7)",  # Green
            "rgba(220, 53, 69, 0.7)",  # Red
            "rgba(255, 193, 7, 0.7)",  # Yellow
            "rgba(13, 202, 240, 0.7)", # Cyan
        ]
        border_colors = [c.replace("0.7", "1") for c in colors]

        indicator = intent.indicator if hasattr(intent, 'indicator') and intent.indicator != 'inconnu' else 'valeur_moyenne'
        if intent.operation == "average":
            indicator = "valeur_moyenne"

        if intent.operation == "trend":
            chart["type"] = "line"
            # Grouper par région si plusieurs régions
            regions = list(set([d.get('region') for d in data if 'region' in d]))
            
            if not regions: # Cas de la moyenne globale
                chart["labels"] = [str(d['annee']) for d in data]
                dataset = {
                    "label": f"Moyenne ({indicator})",
                    "data": [d[indicator] for d in data],
                    "borderColor": border_colors[0],
                    "backgroundColor": colors[0].replace("0.7", "0.1"),
                    "tension": 0.3,
                    "fill": True
                }
                chart["datasets"].append(dataset)
            else:
                # Obtenir toutes les années uniques
                annees = sorted(list(set([d['annee'] for d in data])))
                chart["labels"] = [str(a) for a in annees]
                
                for i, r in enumerate(regions):
                    r_data = [next((item[indicator] for item in data if item.get('region') == r and item['annee'] == a), None) for a in annees]
                    dataset = {
                        "label": str(r),
                        "data": r_data,
                        "borderColor": border_colors[i % len(border_colors)],
                        "backgroundColor": colors[i % len(colors)].replace("0.7", "0.1"),
                        "tension": 0.3,
                        "fill": False
                    }
                    chart["datasets"].append(dataset)

        elif intent.operation in ["compare", "value", "top"]:
            chart["type"] = "bar"
            # Bar chart groupé par année
            annees = sorted(list(set([d['annee'] for d in data])))
            regions = sorted(list(set([d.get('region', 'Global') for d in data])))
            
            if len(annees) == 1:
                chart["labels"] = regions
                dataset = {
                    "label": f"{indicator} ({annees[0]})",
                    "data": [next((item[indicator] for item in data if item.get('region', 'Global') == r), 0) for r in regions],
                    "backgroundColor": [colors[i % len(colors)] for i in range(len(regions))]
                }
                chart["datasets"].append(dataset)
            else:
                chart["labels"] = [str(a) for a in annees]
                for i, r in enumerate(regions):
                    r_data = [next((item[indicator] for item in data if item.get('region', 'Global') == r and item['annee'] == a), 0) for a in annees]
                    dataset = {
                        "label": str(r),
                        "data": r_data,
                        "backgroundColor": colors[i % len(colors)]
                    }
                    chart["datasets"].append(dataset)
        
        return chart

    def _format_table_data(self, data):
        # Arrondir les floats pour l'affichage
        formatted = []
        for item in data:
            new_item = {}
            for k, v in item.items():
                if isinstance(v, float):
                    new_item[k] = round(v, 2)
                else:
                    new_item[k] = v
            formatted.append(new_item)
        return formatted
