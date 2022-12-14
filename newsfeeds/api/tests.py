from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination
from django.conf import settings
from newsfeeds.services import NewsFeedService

NEWSFEED_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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
        self.assertEqual(len(response.data["results"]), 0)

        # you can see your tweets
        self.user1_client.post(POST_TWEETS_URL, {'content': 'Hello, World!'})
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user("followed")
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.user1, tweet = tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        response = self.user1_client.get(NEWSFEED_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(response.data['results'][-1]['id'], newsfeeds[page_size - 1].id)

        response = self.user1_client.get(NEWSFEED_URL,
                                         {'created_at__lt':newsfeeds[page_size - 1].created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(response.data['results'][-1]['id'], newsfeeds[2 * page_size-1].id)

        response = self.user1_client.get(NEWSFEED_URL,
                                         {'created_at__gt':newsfeeds[0].created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.user1, tweet = tweet)

        response = self.user1_client.get(NEWSFEED_URL,
                                         {'created_at__gt':newsfeeds[0].created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.user1.profile
        profile.nickname = "No.1 user"
        profile.save()

        self.assertEqual(self.user2.username, 'user2')
        self.create_newsfeed(self.user1, self.create_tweet(self.user2))
        self.create_newsfeed(self.user1, self.create_tweet(self.user1))

        response = self.user1_client.get(NEWSFEED_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'No.1 user')
        self.assertEqual(results[1]['tweet']['user']['username'], 'user2')

        self.user2.username = 'user No.2'
        self.user2.save()
        profile.nickname = '1user'
        profile.save()

        response = self.user1_client.get(NEWSFEED_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1')
        self.assertEqual(results[0]['tweet']['user']['nickname'], '1user')
        self.assertEqual(results[1]['tweet']['user']['username'], 'user No.2')

    def test_tweet_cache(self):
        tweet = self.create_tweet(user=self.user1, content="original")
        self.create_newsfeed(self.user1, tweet)
        self.create_newsfeed(self.user2, tweet)

        self.user1.username = "user3"
        self.user1.save()
        response = self.user1_client.get(NEWSFEED_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'original')
        self.assertEqual(results[0]['tweet']['user']['username'], 'user3')

        tweet.content = "altered"
        tweet.save()
        response = self.user1_client.get(NEWSFEED_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'altered')
        self.assertEqual(results[0]['tweet']['user']['username'], 'user3')

    def _paginate_to_get_newsfeed(self, client):
        response = client.get(NEWSFEED_URL)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at__lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEED_URL, {'created_at__lt': created_at__lt})
            results.extend(response.data['results'])
        return results

    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = EndlessPagination.page_size
        users = [self.create_user("{}".format(i)) for i in range(5)]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content='from user{}'.format(i % 5))
            newsfeeds.append(self.create_newsfeed(self.user1, tweet))
        newsfeeds = newsfeeds[::-1]

        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        queryset = NewsFeed.objects.filter(user=self.user1)
        self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeed(self.user1_client)
        self.assertEqual(len(results), list_limit+page_size)

        for i in range(list_limit+page_size):
            self.assertEqual(newsfeeds[i].id, results[i]['id'])

        self.create_friendship(self.user1, self.user2)
        tweet = self.create_tweet(self.user2)
        NewsFeedService.fanout_to_followers(tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeed(self.user1_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]['tweet']['id'], tweet.id)
            for i in range(1, list_limit + page_size):
                self.assertEqual(results[i]['id'], newsfeeds[i-1].id)

        _test_newsfeeds_after_new_feed_pushed()

        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()
















