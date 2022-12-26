from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
# check whether username and password exist

class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source="profile.nickname")
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

class UserSerializerForTweets(UserSerializerWithProfile):
    pass

class UserSerializerForComments(UserSerializerWithProfile):
    pass

class UserSerializerForLike(UserSerializerWithProfile):
    pass

class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


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
        user.profile
        return user

class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')
