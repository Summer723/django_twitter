from testing.testcases import TestCase
from inbox.services import NotificationService
from notifications.models import Notification


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()

        self.summer, self.summer_client = self.create_user_and_client('summer')
        self.wang, self.wang_client = self.create_user_and_client('wang')
        self.tweet = self.create_tweet(self.summer)

    def test_send_comment_notification(self):
        comment = self.create_comment(self.summer, self.tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        comment = self.create_comment(self.wang, self.tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        like = self.create_like(self.summer, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        like = self.create_like(self.wang, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)
