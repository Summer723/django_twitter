from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

NEWSFEED_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user("user1")
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user("user2")
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list(self):
        # have to log in to check news feed
        # response will be the something like you defined in serializers
        # here we define serializer be (id, created at, tweet)
        # where tweet is going to show the content define
        # in tweet serializer
        response = self.anonymous_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 403)
        # have to use get not post
        response = self.user1_client.post(NEWSFEED_URL)
        self.assertEqual(response.status_code, 405)
        # get nothing
        response = self.user1_client.get(NEWSFEED_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 0)

        # you can see your tweets
        self.user1_client.post(POST_TWEETS_URL, {'content': 'Hello, World!'})
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 1)

        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)






