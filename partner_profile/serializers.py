from rest_framework import serializers

class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)

class PartnerStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    partner_id = serializers.UUIDField(allow_null=True)
    partner_name = serializers.CharField(allow_null=True)
