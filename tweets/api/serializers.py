from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer,UserSerializerForTweets

class TweetSerializer(serializers.ModelSerializer):
    user =  UserSerializerForTweets()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6,max_length=140)

    # This tells django, which model we are using and which feature of the model we
    # should use
    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):

        # context comes with thte serializere
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user = user, content = content)
        return tweet
