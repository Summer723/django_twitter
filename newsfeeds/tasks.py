from celery import shared_task
from friendships.services import FriendshipService
from utils.time_constants import ONE_HOUR
from newsfeeds.models import NewsFeed
from tweets.models import Tweet

@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(task_id):
    from newsfeeds.services import NewsFeedService

    # filter returns a queryset
    # get return the object of the queryset
    tweet = Tweet.objects.filter(id=task_id)
    tweet = Tweet.objects.get(id=task_id)

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
    # bulk_create will not trigger post_save()
    NewsFeed.objects.bulk_create(newsfeeds)

    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)



