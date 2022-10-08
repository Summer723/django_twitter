from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # 这个函数会在每个 test function 执行的时候被执行
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )
    # it is not start with test_, it will not automatically run
    def createUser(self, username, email, password):
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

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
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
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

        # check signin info
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
