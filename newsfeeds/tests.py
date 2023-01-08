from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from django_twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient
from newsfeeds.tasks import fanout_newsfeeds_main_task
from newsfeeds.models import NewsFeed


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

    class NewsFeedTaskTests(TestCase):

        def setUp(self):
            self.clear_cache()
            self.linghu = self.create_user('linghu')
            self.dongxie = self.create_user('dongxie')

        def test_fanout_main_task(self):
            tweet = self.create_tweet(self.linghu, 'tweet 1')
            self.create_friendship(self.dongxie, self.linghu)
            msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
            self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created.')
            self.assertEqual(1 + 1, NewsFeed.objects.count())
            cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
            self.assertEqual(len(cached_list), 1)

            for i in range(2):
                user = self.create_user('user{}'.format(i))
                self.create_friendship(user, self.linghu)
            tweet = self.create_tweet(self.linghu, 'tweet 2')
            msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
            self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created.')
            self.assertEqual(4 + 2, NewsFeed.objects.count())
            cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
            self.assertEqual(len(cached_list), 2)

            user = self.create_user('another user')
            self.create_friendship(user, self.linghu)
            tweet = self.create_tweet(self.linghu, 'tweet 3')
            msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
            self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created.')
            self.assertEqual(8 + 3, NewsFeed.objects.count())
            cached_list = NewsFeedService.get_cached_newsfeeds(self.linghu.id)
            self.assertEqual(len(cached_list), 3)
            cached_list = NewsFeedService.get_cached_newsfeeds(self.dongxie.id)
            self.assertEqual(len(cached_list), 3)
