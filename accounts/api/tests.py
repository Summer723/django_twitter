from django.test import TestCase

#
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
# Create your tests here.

class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@summer.com',
            password='correct password',
        )

    def create_user(self,username, email, password):
        # cannot use User.objects.create*(
        # password needs to be encrypted
        return User.objects.create_user(username, email, password)