from friendships.models import Friendship
from django.contrib.auth.models import User


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # one way to write it
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendships.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # the other way to do it
        # double-check how prefetch_related works
        friendships = Friendship.objects.filter(
            to_user=user
        ).prefetch_related("from_user")
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()
