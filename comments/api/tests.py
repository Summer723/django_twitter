from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from comments.models import Comment


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self) -> None:
        self.summer = self.create_user('Summer')
        self.summer_client = APIClient()
        self.wang = self.create_user('wangge')
        self.wang_client = APIClient()
        self.summer_client.force_authenticate(self.summer)
        self.wang_client.force_authenticate(self.wang)

        self.tweet = self.create_tweet(self.summer)

    def test_create(self):
        # you have to log in to create a comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # you have to specify which tweet you want to comment on
        response = self.summer_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # you cannot comment nothing
        response = self.summer_client.post(COMMENT_URL, {'tweet_id':self.tweet.id})
        self.assertEqual(response.status_code, 400)


        response = self.summer_client.post(COMMENT_URL, {'content': "1"})
        self.assertEqual(response.status_code, 400)

        response = self.summer_client.post(COMMENT_URL, {"content": '1' * 141})
        self.assertEqual(response.status_code,400)
        self.assertEqual('content' in response.data['errors'], True)

        response = self.summer_client.post(COMMENT_URL, {
                                                            'tweet_id': self.tweet.id,
                                                            'content': "yes",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.summer.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'],"yes")


    def test_update(self):
        comment = self.create_comment(self.summer, self.tweet)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        response = self.wang_client.delete(url)
        self.assertEqual(response.status_code, 403)

        count = Comment.objects.count()
        response = self.summer_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_destroy(self):
        comment = self.create_comment(self.summer, self.tweet, 'original')
        another_tweet = self.create_tweet(self.wang)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        # cannot update the comment without logging in
        response = self.anonymous_client.put(url, {'content': "new"})
        self.assertEqual(response.status_code, 403)

        # cannot update the comment that others left
        response = self.wang_client.put(url, {'content': "new"})
        self.assertEqual(response.status_code, 403)

        comment.refresh_from_db()
        self.assertNotEqual(comment.content, "new")

        # you can only update comment section
        old_updated_at = comment.updated_at
        old_created_at = comment.created_at
        now = timezone.now()

        response = self.summer_client.put(url,{
                                                'content': "new",
                                                'user_id': self.summer.id,
                                                'tweet_id': self.tweet.id,
                                                'created_at': now,
                                            })
        self.assertEqual(response.status_code,200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.summer)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertNotEqual(comment.created_at, now)
        self.assertEqual(comment.created_at, old_created_at)
        self.assertNotEqual(comment.updated_at, old_updated_at)



