from django.contrib.auth.models import User
from django.db import models
from tweets.models import Tweet
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from utils.memcached_helper import Memcached_helper

# Create your models here.

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', "created_at"),)

    def __str__(self):
        return '{} - {} Says {} under the Tweet {}'.format(
            self.created_at,
            self.user,
            self.content,
            self.tweet,
        )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return Memcached_helper.get_object_through_cache(User, self.user_id)