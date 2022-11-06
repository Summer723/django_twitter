from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.summer, self.summer_client = self.create_user_and_client('summer')
        self.wang, self.wang_client = self.create_user_and_client('wang')
        self.tweet = self.create_tweet(self.summer)


    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.summer_client.post(COMMENT_URL, {
                                    'tweet_id' : self.tweet.id,
                                    'content': 'For tests!',
                                })
        self.assertEqual(Notification.objects.count(), 0)
        self.wang_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': 'For tests!',
        })
        self.assertEqual(Notification.objects.count(), 1)


    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.summer_client.post(LIKE_URL, {
                                    'content_type' : 'tweet',
                                    'object_id': self.tweet.id,
                                })
        self.assertEqual(Notification.objects.count(), 0)
        self.wang_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)


