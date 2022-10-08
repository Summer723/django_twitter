from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


# Create your tests here.
class TweetTests(TestCase):

    def test_hours_to_now(self):
        wanggie = User.objects.create_user(username= "Wanggie")
        tweet = Tweet.objects.create(user=wanggie, content='小心王哥往你脸上')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now,10)
