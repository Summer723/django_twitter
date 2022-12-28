from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase
from tweets.models import TweetPhoto
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus


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
            tweet= self.tweet,
            user=self.summer,
        )
        self.assertEqual(photo.user, self.summer)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

