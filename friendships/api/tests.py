from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import MyPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        # self.anonymous_client = APIClient()
        self.clear_cache()
        self.client1 = self.create_user("client1")
        self.client1_client = APIClient()
        self.client1_client.force_authenticate(self.client1)

        self.client2 = self.create_user("client2")
        self.client2_client = APIClient()
        self.client2_client.force_authenticate(self.client2)
        for i in range(2):
            follower = self.create_user("client2 follower{}".format(i))
            Friendship.objects.create(from_user=follower, to_user=self.client2)

        for i in range(3):
            following = self.create_user("client2 following{}".format(i))
            Friendship.objects.create(from_user=self.client2, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.client1.id)

        # you have to sign in to follow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # you should not use get to follow, but post
        response = self.client2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # you cannot follow yourself
        response = self.client1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # succeed
        response = self.client2_client.post(url)
        self.assertEqual(response.status_code, 201)

        # repeat following the same one
        response = self.client2_client.post(url)
        self.assertEqual(response.status_code, 400)

        # count
        count = Friendship.objects.count()
        response = self.client1_client.post(FOLLOW_URL.format(self.client2.id))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.client1.id)

        # you need to log in to unfollow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # should not use get to unfollow others
        response = self.client2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # cannot unfollow yourself
        response = self.client1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # unfollow succeeded
        Friendship.objects.create(from_user=self.client2, to_user=self.client1)
        count = Friendship.objects.count()
        response = self.client2_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # silence when you unfollow somebody you are not following
        response = self.client1_client.post(UNFOLLOW_URL.format(self.client2.id))
        count = Friendship.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_following(self):
        url = FOLLOWINGS_URL.format(self.client2.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

        # make sure that data is ordered by the time they are  created
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(response.data['results'][0]['user']['username'],
                         'client2 following2')
        self.assertEqual(response.data['results'][1]['user']['username'],
                         'client2 following1')
        self.assertEqual(response.data['results'][2]['user']['username'],
                         'client2 following0')

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.client2.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        # make sure that data is ordered by the time they are  created
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['results'][0]['user']['username'],
                         'client2 follower1')
        self.assertEqual(response.data['results'][1]['user']['username'],
                         'client2 follower0')
    def test_followers_pagination(self):
        max_page_size = MyPagination.max_page_size
        page_size = MyPagination.page_size
        for i in range(page_size * 2):
            follower = self.create_user("client1_followers{}".format(i))
            Friendship.objects.create(from_user=follower, to_user=self.client1)
            Friendship.objects.create(from_user=self.client1, to_user=follower)

            if follower.id % 2 == 0:
                Friendship.objects.create(from_user=follower, to_user=self.client2)
                Friendship.objects.create(from_user=self.client2, to_user=follower)

        url = FOLLOWERS_URL.format(self.client1.id)
        response = self.anonymous_client.get(url, {"page": 1})
        for result in response.data["results"]:
            self.assertEqual(result["has_followed"], False)

        response = self.client2_client.get(url, {'page': 1})
        for result in response.data["results"]:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        response = self.client1_client.get(url, {'page': 1})
        for result in response.data["results"]:
            self.assertEqual(result['has_followed'], True)


    def test_followings_pagination(self):
        max_page_size = MyPagination.max_page_size
        page_size = MyPagination.page_size
        for i in range(page_size * 2):
            following = self.create_user("client1_followings{}".format(i))
            Friendship.objects.create(from_user=self.client1, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(from_user=self.client2, to_user=following)

        url = FOLLOWINGS_URL.format(self.client1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        response = self.anonymous_client.get(url, {"page": 1})
        for result in response.data["results"]:
            self.assertEqual(result["has_followed"], False)

        response = self.client2_client.get(url, {'page': 1})
        for result in response.data["results"]:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        response = self.client1_client.get(url, {'page': 1})
        for result in response.data["results"]:
            self.assertEqual(result['has_followed'], True)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        response = self.anonymous_client.get(url, {'page': 1, 'page_size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {
            'page': 1,
            'page_size': 2,
        })
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
