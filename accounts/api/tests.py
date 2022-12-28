from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = "/api/profiles/{}/"

class AccountApiTests(TestCase):

    def setUp(self):
        self.clear_cache()

        # 这个函数会在每个 test function 执行的时候被执行
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    # if it is not start with test_, it will not automatically run
    def test_login(self):
        # 每个测试函数必须以 test_ 开头，才会被自动调用进行测试
        # 测试必须用 post 而不是 get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 登陆失败，http status code 返回 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # 用了 post 但是密码错了
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # 验证还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # 用正确的密码
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        # self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        self.assertEqual(response.data['user']['id'], self.user.id)
        # 验证已经登录了
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # first log in
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': "correct password",
        })

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True)

        # we have to use "post" to access it
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], False)

    def test_signup(self):
        user_info = {
            'username': "somebody",
            'email': 'somebody@summer.com',
            'password': 'any password',
        }

        response = self.client.get(SIGNUP_URL, user_info)
        self.assertEqual(response.status_code, 405)

        # test when the username is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 's',
            'email' : 'wangge@summer.com',
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 400)

        # test when the email is wrong
        response = self.client.post(SIGNUP_URL, {
            'username': 'summersheng',
            'email': 'wangge summer.com',
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 400)

        # test when password is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'summersheng',
            'email': 'wangge@summer.com',
            'password': '123'
        })
        self.assertEqual(response.status_code, 400)

        # sign up correctly and check the status
        response = self.client.post(SIGNUP_URL, user_info)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data['user']['username'], 'somebody')

        user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=user_id).first()
        self.assertNotEqual(profile, None)

        # check signin info
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


class UserProfileAPITests(TestCase):
    def test_update(self):
        summer, summer_client = self.create_user_and_client('summer')
        prof = summer.profile
        prof.nickname = "old nickname"
        prof.save()
        url = USER_PROFILE_DETAIL_URL.format(prof.id)

        _,wang_client = self.create_user_and_client('wang')
        response = wang_client.put(url, {"nickname":'new nickname',})

        self.assertEqual(response.status_code, 403)
        prof.refresh_from_db()
        self.assertEqual(prof.nickname, 'old nickname')

        response = summer_client.put(url, {"nickname": 'new nickname', })
        self.assertEqual(response.status_code, 200)
        prof.refresh_from_db()
        self.assertEqual(prof.nickname, 'new nickname')

        response = summer_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        prof.refresh_from_db()
        self.assertIsNotNone(prof.avatar)

