from apps.statistics.models import StatistiqueRegionale
from django.db.models import Avg, Sum
from apps.chatbot.nlp.intent_parser import QueryIntent

class StatistiqueRepository:
    def execute_query(self, intent: QueryIntent):
        qs = StatistiqueRegionale.objects.all()

        # Filtrer par région si spécifié
        if intent.regions:
            qs = qs.filter(region__in=intent.regions)

        # Filtrer par année(s)
        if intent.operation == "trend" and intent.start_year and intent.end_year:
            qs = qs.filter(annee__range=[intent.start_year, intent.end_year])
            # Ordonner pour le graphique de tendance
            qs = qs.order_by('annee')
        elif intent.start_year:
            qs = qs.filter(annee=intent.start_year)

        # Récupérer les données demandées
        indicator = intent.indicator
        
        # Si l'indicateur est inconnu, on récupère un ensemble de base ou on limite
        if indicator == "inconnu" or not hasattr(StatistiqueRegionale, indicator):
            indicator = "population" # fallback

        # Si l'opération est une moyenne sur toutes les régions
        if intent.operation == "average":
            result = qs.values('annee').annotate(valeur_moyenne=Avg(indicator)).order_by('annee')
            return list(result), qs.count()

        # Si l'opération est un classement (Top N)
        if intent.operation == "top":
            # On trie de manière décroissante par défaut, en limitant aux 5 premiers par exemple
            fields = ['region', 'annee', indicator]
            data = list(qs.values(*fields).order_by(f'-{indicator}')[:5])
            return data, qs.count()

        # Récupération classique
        fields = ['region', 'annee', indicator]
        data = list(qs.values(*fields).order_by('annee', 'region'))
        
        return data, qs.count()
