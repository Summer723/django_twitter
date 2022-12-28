from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def test_comment(self):
        user = self.create_user('linghu')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)

    def setUp(self):
        self.clear_cache()
        self.summer = self.create_user('summer')
        self.tweet = self.create_tweet(self.summer, content="This is a test for tweet!")
        self.comment = self.create_comment(self.summer, self.tweet, content="This is a test for comment!")

    def test_like_set(self):
        self.create_like(self.summer, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.summer, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.create_user('random'), self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
