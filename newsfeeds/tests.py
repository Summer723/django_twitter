from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from django_twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


class NewsFeedServicerTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.summer = self.create_user('summer')
        self.wang = self.create_user('wang')

    def test_get_user_newsfeeds(self):
        newsfeeds_ids = []
        for i in range (3):
            tweet = self.create_tweet(self.wang)
            newsfeed = self.create_newsfeed(self.summer, tweet)
            newsfeeds_ids.append(newsfeed.id)
        newsfeeds_ids = newsfeeds_ids[::-1]

        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.summer.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeeds_ids)

        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.summer.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeeds_ids)

        new_tweet = self.create_tweet(self.wang)
        new_newsfeed = self.create_newsfeed(self.summer, new_tweet)
        newsfeeds_ids.insert(0, new_newsfeed.id)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.summer.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeeds_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        feed1 = self.create_newsfeed(self.summer, self.create_tweet(self.summer))

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id = self.summer.id)
        self.assertEqual(conn.exists(key), False)

        feed2 = self.create_newsfeed(self.summer, self.create_tweet(self.summer))

        self.assertEqual(conn.exists(key), True)

        feeds = NewsFeedService.get_cached_newsfeeds(self.summer.id)
        self.assertEqual([f.id for f in feeds], [feed2.id, feed1.id])


