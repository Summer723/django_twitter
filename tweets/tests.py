from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase
from tweets.models import TweetPhoto
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from tweets.services import TweetService
from django_twitter.cache import USER_TWEETS_PATTERN


# Create your tests here.
class TweetTests(TestCase):

    def test_hours_to_now(self):
        wanggie = User.objects.create_user(username= "Wanggie")
        tweet = Tweet.objects.create(user=wanggie, content='小心王哥往你脸上')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now,10)

    def setUp(self):
        self.clear_cache()

        self.summer = self.create_user('summer')
        self.tweet = self.create_tweet(self.summer, content="This is a test for tweet!")
        self.comment = self.create_comment(self.summer, self.tweet, content="This is a test for comment!")

    def test_like_set(self):
        self.create_like(self.summer, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.summer, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.create_user('random'), self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.summer,
        )
        self.assertEqual(photo.user, self.summer)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.summer)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data = conn.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)


class TweetServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.summer = self.create_user('summer')
        self.wang = self.create_user("wang")

    def test_get_user_tweets(self):
        tweets_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.summer, content="Tweet".format(i))
            tweets_ids.append(tweet.id)
        tweets_ids = tweets_ids[::-1]

        conn = RedisClient.get_connection()
        tweets = TweetService.get_cached_tweet(self.summer.id)
        self.assertEqual(tweets_ids, [t.id for t in tweets])

        tweets = TweetService.get_cached_tweet(self.summer.id)
        self.assertEqual([t.id for t in tweets], tweets_ids)


        new_tweet = self.create_tweet(self.summer, content='new tweet')
        tweets_ids.insert(0, new_tweet.id)
        tweets = TweetService.get_cached_tweet(self.summer.id)
        self.assertEqual(tweets_ids, [t.id for t in tweets])

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.summer, "first")

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_TWEETS_PATTERN.format(user_id=self.summer.id)
        self.assertEqual(conn.exists(key), False)

        tweet2 = self.create_tweet(self.summer, 'second')
        self.assertEqual(conn.exists(key), True)

        tweets = TweetService.get_cached_tweet(self.summer.id)

        self.assertEqual([t.id for t in tweets], [tweet2.id, tweet1.id])

