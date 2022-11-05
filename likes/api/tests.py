from testing.testcases import TestCase
from rest_framework import status



LIKE_BASE_URL = '/api/likes/'
CANCEL_BASE_URL = '/api/likes/cancel/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.summer, self.summer_client = self.create_user_and_client('summer')
        self.wang, self.wang_client = self.create_user_and_client('wang')

    def test_tweet_likes(self):
        # test when it does not specifies content type
        tweet = self.create_tweet(self.wang)
        data = {"content_type": 'tweet', 'object_id':tweet.id}
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.summer_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.summer_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.summer_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.wang_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        # test when it does not specifies content type
        tweet = self.create_tweet(self.summer)
        comment = self.create_comment(self.wang, tweet)
        data = {"content_type": 'comment' , 'object_id': comment.id}
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.summer_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.summer_client.post(LIKE_BASE_URL, {
            'content_type':'video',
            'object_id':comment.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('content_type' in response.data['errors'], True)

        response = self.summer_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('object_id' in response.data['errors'], True)

        response = self.summer_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(comment.like_set.count(), 1)

        response = self.summer_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        response = self.wang_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.summer)
        comment = self.create_comment(self.wang, tweet)
        comment_data = {"content_type": 'comment', 'object_id': comment.id}
        tweet_data = {"content_type": 'tweet', 'object_id': tweet.id}

        self.summer_client.post(LIKE_BASE_URL, comment_data)
        self.wang_client.post(LIKE_BASE_URL, tweet_data)

        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        response = self.anonymous_client.post(CANCEL_BASE_URL, comment_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.post(CANCEL_BASE_URL, tweet_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.summer_client.get(CANCEL_BASE_URL, comment_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.wang_client.get(CANCEL_BASE_URL, tweet_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.summer_client.post(CANCEL_BASE_URL, comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.like_set.count(), 0)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.wang_client.post(CANCEL_BASE_URL, tweet_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.like_set.count(), 0)
        self.assertEqual(tweet.like_set.count(), 0)







