# def incr_likes_count(sender, instance, created, **kwargs):
#     from tweets.models import Tweet
#     from django.db.models import F
#
#     if not created:
#         return
#
#     model_class = instance.content_type.model_class()
#     if model_class != Tweet:
#         return
#
#     Tweet.objects.filter(
#         id=instance.object_id
#     ).update(comments_count=F("comments_count") + 1)
#
#
# def decr_likes_count(sender, instance, created, **kwargs):
#     from tweets.models import Tweet
#     from django.db.models import F
#
#     model_class = instance.content_type.model_class()
#     if model_class != Tweet:
#         return
#
#     Tweet.objects.filter(
#         id=instance.object_id
#     ).update(comments_count=F("comments_count") - 1)
from utils.listeners import invalidate_object_cache


def incr_comments_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    # handle new comment
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') + 1)
    # invalidate_object_cache(sender=Tweet, instance=instance.tweet)


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    # handle comment deletion
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') - 1)
    # invalidate_object_cache(sender=Tweet, instance=instance.tweet)