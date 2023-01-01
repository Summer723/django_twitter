from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from rest_framework.test import APIClient
from comments.models import Comment
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from newsfeeds.models import NewsFeed
from django.core.cache import caches
from utils.redis_client import RedisClient
from friendships.models import Friendship


class TestCase(DjangoTestCase):

    def clear_cache(self):
        RedisClient.clear()
        caches['testing'].clear()


    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = "generic password"
        if email is None:
            email = f"{username}@twitter.com"

        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default content for test'

        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = "A default comment!"
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        # this returns the instance and whether it is newly created or not 
        instance, _ = Like.objects.get_or_create(
            # here we throw in the name of the class, which is a model, which is not
            # what we need
            # then, get_for_model will return its content type, which is what we need
            content_type=ContentType.objects.get_for_model(target.__class__),
            user=user,
            object_id=target.id,
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_friendship(self, user1, user2):
        return Friendship.objects.create(from_user=user1, to_user=user2)
