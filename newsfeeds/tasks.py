from celery import shared_task
from friendships.services import FriendshipService
from utils.time_constants import ONE_HOUR
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from newsfeeds.constants import FANOUT_BATCH_SIZE

@shared_task(routing_key="default",time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    from newsfeeds.services import NewsFeedService

    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    followers = FriendshipService.get_followers_id(tweet_user_id)

    index = 0
    while index < len(followers):
        batch = followers[index:index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch)
        index += FANOUT_BATCH_SIZE

    return '{} newsfeeds going to fanout, {} batches created.'.format(
        len(followers),
        (len(followers) - 1) // FANOUT_BATCH_SIZE + 1,
    )


@shared_task(routing_key="newsfeed", time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, followers_id):
    from newsfeeds.services import NewsFeedService
    newsfeeds = [NewsFeed(user_id=follower_id, tweet_id=tweet_id)
                 for follower_id in followers_id]
    NewsFeed.objects.bulk_create(newsfeeds)
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
    return "{} newsfeeds created".format(len(newsfeeds))

    # from newsfeeds.services import NewsFeedService
    #
    # # filter returns a queryset
    # # get return the object of the queryset
    # tweet = Tweet.objects.filter(id=task_id)
    # tweet = Tweet.objects.get(id=task_id)
    #
    # followers = FriendshipService.get_followers(tweet.user)
    #
    # # for + query will be really SLOW
    # # for follower in followers:
    # #     NewsFeed.objects.create(user=follower, tweet=tweet)
    # # better if you bulk-create newsfeeds
    # newsfeeds = [
    #     NewsFeed(user=follower, tweet=tweet)
    #     for follower in followers
    # ]
    # newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    # # bulk_create will not trigger post_save()
    # NewsFeed.objects.bulk_create(newsfeeds)
    #
    # for newsfeed in newsfeeds:
    #     NewsFeedService.push_newsfeed_to_cache(newsfeed)
    #
    #
    #
