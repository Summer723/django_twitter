from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'email')
# check whether username and password exist
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()