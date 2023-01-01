from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.memcached_helper import Memcached_helper
from newsfeeds.listeners import push_newsfeed_to_cache
from django.db.models.signals import post_save
# Create your models here.


class NewsFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'

    @property
    def cached_tweet(self):
        return Memcached_helper.get_object_through_cache(Tweet, self.tweet_id)


post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)
