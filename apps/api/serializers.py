from rest_framework import serializers

class QuestionRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, help_text="La question posée par l'utilisateur.")

class ChartDatasetSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField(allow_null=True))

class ChartDataSerializer(serializers.Serializer):
    type = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=ChartDatasetSerializer())

class MetadataSerializer(serializers.Serializer):
    fictitious = serializers.BooleanField(default=True)
    rows_used = serializers.IntegerField()

class QuestionResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    table = serializers.ListField(child=serializers.DictField())
    chart = ChartDataSerializer(allow_null=True)
    metadata = MetadataSerializer()
