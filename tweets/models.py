from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from utils.memcached_helper import Memcached_helper
from django.db.models.signals import pre_save, post_delete, post_save
from utils.listeners import invalidate_object_cache
from tweets.listeners import push_tweet_to_cache


# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='The user who created this tweet.',
    )
    # can add " db_index = True", django will index it for you
    content = models.CharField(max_length=255)
    # auto_now_add means it will return the time it created
    created_at = models.DateTimeField(auto_now_add=True)

    # For new added fields null = True must be set
    # otherwise the whole sheet would be locked
    likes_count = models.IntegerField(default=0, null=True)
    comments_count = models.IntegerField(default=0, null=True)

    class Meta:
        # sheet 内部的排列方式
        # 联合索引
        # 相当于 新建了一个表单 with
        # user          created_at       user_id
        index_together = (('user', 'created_at'), )
        # 展示时的排序
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        from accounts.services import UserService
        return Memcached_helper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    file = models.FileField()
    order = models.IntegerField(default=0)

    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet.id}: {self.file}'

pre_save.connect(invalidate_object_cache, sender= Tweet)
post_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache, sender=Tweet)
