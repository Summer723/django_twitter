from notifications.models import Notification
from testing.testcases import TestCase
from rest_framework import status


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.clear_cache()

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

class NotificationApiTests(TestCase):
    def setUp(self) -> None:
        self.summer, self.summer_client = self.create_user_and_client('summer')
        self.wang, self.wang_client = self.create_user_and_client('wang')
        self.summertweet = self.create_tweet(self.summer)

        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_unread_count(self):
        self.wang_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.summertweet.id
        })
        self.wang_client.post(COMMENT_URL,{
            'tweet_id': self.summertweet.id,
            'content': "LOL"
        })
        url = '/api/notifications/unread-count/'
        response = self.summer_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.summer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.wang_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.summertweet.id
        })
        self.wang_client.post(COMMENT_URL, {
            'tweet_id': self.summertweet.id,
            'content': "LOL"
        })
        url = '/api/notifications/mark-all-as-read/'
        response = self.summer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.summer_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_count'], 2)

        unread_url = '/api/notifications/unread-count/'
        response = self.summer_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.wang_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.summertweet.id,
        })
        comment = self.create_comment(self.summer, self.summertweet)
        self.wang_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.summer_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.summer_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.summer_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.summer_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_update(self):
        self.wang_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.summertweet.id,
        })
        comment = self.create_comment(self.summer, self.summertweet)
        self.wang_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        notification = self.summer.notifications.first()

        url = "/api/notifications/{}/".format(notification.id)
        response = self.summer_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.wang_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.summer_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread_url = '/api/notifications/unread-count/'
        response = self.summer_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        response = self.summer_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.summer_client.put(url, {'unread': False, 'verb': 'newverb'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertNotEqual(response.data['verb'], 'newverb')
