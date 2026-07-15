"""Sérialiseurs pour définir le contrat JSON strict de l'API."""
from rest_framework import serializers


class QuestionRequestSerializer(serializers.Serializer):
    """Entrée de l'endpoint POST /api/question/."""

    question = serializers.CharField(
        required=True,
        help_text="La question posée par l'utilisateur en langage naturel.",
    )


class ChartDatasetSerializer(serializers.Serializer):
    """Un jeu de données pour Chart.js (une courbe ou une série de barres)."""

    label = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField(allow_null=True))


class ChartDataSerializer(serializers.Serializer):
    """Données complètes pour un graphique Chart.js."""

    type = serializers.CharField(help_text="Type de graphique : bar, line.")
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=ChartDatasetSerializer())


class MetadataSerializer(serializers.Serializer):
    """Métadonnées de la réponse."""

    fictitious = serializers.BooleanField(
        default=True, help_text="Indique que les données sont fictives (pédagogiques)."
    )
    rows_used = serializers.IntegerField(help_text="Nombre de lignes utilisées.")


class QuestionResponseSerializer(serializers.Serializer):
    """Sortie de l'endpoint POST /api/question/ — contrat JSON figé."""

    answer = serializers.CharField(help_text="Réponse textuelle en français.")
    table = serializers.ListField(
        child=serializers.DictField(), help_text="Données sources en tableau."
    )
    chart = ChartDataSerializer(
        allow_null=True, help_text="Données Chart.js (null si pas de graphique)."
    )
    metadata = MetadataSerializer()
