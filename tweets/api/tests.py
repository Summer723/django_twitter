from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet,TweetPhoto
from django.core.files.uploadedfile import SimpleUploadedFile

TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    def setUp(self):
        # create three uses
        #self.anonymous_client = APIClient()

        # create use1 and his tweets
        self.user1 = self.create_user('user1', 'user1@twitter.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.tweet = self.create_tweet(self.user1)

        self.user2 = self.create_user('user2', 'user2@twitter.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]


    def test_list_api(self):
        # first test that it has to comes with id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # it comes with id
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 4)

        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 2)

        # check their ordering
        self.assertEqual(response.data["tweets"][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data["tweets"][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        response = self.anonymous_client.post(TWEET_CREATE_API, {'content':"something"})
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(TWEET_CREATE_API, {'content': "one"})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(TWEET_CREATE_API, {
                'content': "one" * 200
        })
        self.assertEqual(response.status_code, 400)

        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
                'content': "This is a tweet!"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        response = self.anonymous_client.get(TWEET_RETRIEVE_API.format(-1))
        self.assertEqual(response.status_code, 404)

        response = self.user1_client.get(TWEET_RETRIEVE_API.format(self.tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)


        self.create_comment(self.user1, self.tweet, "i love it")
        self.create_comment(self.user2, self.tweet, "me too")
        self.create_comment(self.user1, self.create_tweet(self.user1), "+10086")
        response = self.user1_client.get(TWEET_RETRIEVE_API.format(self.tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 2)


    def test_create_with_files(self):
        # 上传空文件列表
        # response = self.user1_client.post(TWEET_CREATE_API, {
        #     'content': 'a selfie',
        #     'files': [],
        # })
        # self.assertEqual(response.status_code, 201)
        # self.assertEqual(TweetPhoto.objects.count(), 0)
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'a selfie',
            'files': [],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        file = SimpleUploadedFile(
            name = "a file",
            content=str.encode('a fake image'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'a selfie',
            'files': [file],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # 测试多个文件上传
        file1 = SimpleUploadedFile(
            name='selfie1.jpg',
            content=str.encode('selfie 1'),
            content_type='image/jpeg',
        )
        file2 = SimpleUploadedFile(
            name='selfie2.jpg',
            content=str.encode('selfie 2'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'two selfies',
            'files': [file1, file2],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)

        # 从读取的 API 里确保已经包含了 photo 的地址
        retrieve_url = TWEET_RETRIEVE_API.format(response.data['id'])
        response = self.user1_client.get(retrieve_url)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('selfie1' in response.data['photo_urls'][0], True)
        self.assertEqual('selfie2' in response.data['photo_urls'][1], True)

        # 测试上传超过 9 个文件会失败
        files = [
            SimpleUploadedFile(
                name=f'selfie{i}.jpg',
                content=str.encode(f'selfie{i}'),
                content_type='image/jpeg',
            )
            for i in range(10)
        ]
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'failed due to number of photos exceeded limit',
            'files': files,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)