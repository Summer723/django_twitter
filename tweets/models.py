from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from django.contrib.contenttypes.models import ContentType
from likes.models import Like


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
