from testing.testcases import TestCase
from rest_framework.test import APIClient


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

