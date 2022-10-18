from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)

        # for + query will be really SLOW
        # for follower in followers:
        #     NewsFeed.objects.create(user=follower, tweet=tweet)
        # better if you bulk-create newsfeeds
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in followers
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
        