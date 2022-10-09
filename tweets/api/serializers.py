from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer,UserSerializerForTweets

class TweetSerializer(serializers.ModelSerializer):
    user =  UserSerializerForTweets()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')