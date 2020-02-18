from rest_framework import serializers


class ReadMessageSerializer(serializers.Serializer):
    token = serializers.CharField()
    phone = serializers.CharField()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class AutoconnectSerializer(serializers.Serializer):
    token = serializers.CharField()
    set = serializers.CharField(max_length=1, required=False)


class SendMessageSerializer(serializers.Serializer):
    token = serializers.CharField()
    phone = serializers.CharField()
    message = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
