from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        self.summer = self.create_user('summer')
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = self.summer.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)