from rest_framework import serializers

class QuestionRequestSerializer(serializers.Serializer):
    question = serializers.CharField(
        max_length=500, 
        required=True,
        help_text="La question posée par l'utilisateur."
    )

class MetadataSerializer(serializers.Serializer):
    fictitious = serializers.BooleanField()
    rows_used = serializers.IntegerField()

class ChartDatasetSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField())
    backgroundColor = serializers.CharField(required=False)
    borderColor = serializers.CharField(required=False)
    borderWidth = serializers.IntegerField(required=False)
    tension = serializers.FloatField(required=False)

class ChartSerializer(serializers.Serializer):
    type = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    datasets = ChartDatasetSerializer(many=True)

class QuestionResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    table = serializers.ListField(child=serializers.DictField())
    chart = ChartSerializer(allow_null=True)
    metadata = MetadataSerializer()
