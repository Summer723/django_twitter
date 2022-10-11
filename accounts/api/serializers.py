from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
# check whether username and password exist


class UserSerializerForTweets(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("username", "password", 'email')


    # will be called when is_validate is called
    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'Message': 'This username has been registered.'
            })

        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'Message': 'This email address has been registered.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        password = validated_data['password']
        email = validated_data['email'].lower()

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
