from utils.redis_helper import RedisHelper


def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    Tweet.objects.filter(
        id=instance.object_id
    ).update(likes_count=F("likes_count") + 1)
    RedisHelper.incr_count(instance.content_object, "likes_count")


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    Tweet.objects.filter(
        id=instance.object_id
    ).update(likes_count=F("likes_count") - 1)
    RedisHelper.decr_count(instance.content_object, "likes_count")

