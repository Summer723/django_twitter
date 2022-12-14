from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from utils.memcached_helper import Memcached_helper
from django.db.models.signals import post_save, pre_delete
from likes.listeners import incr_likes_count, decr_likes_count


# Create your models here.
class Like(models.Model):
    # from which user
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()  # tweet id or comment id
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )

    content_object = GenericForeignKey('content_type', "object_id")
    # the time the like got created
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (
            ('content_type', 'object_id', "created_at"),
            ('user', 'content_type', "created_at"),
        )

    def __str__(self):
        return "At {}, {} liked {} {}".format(
                                              self.created_at,
                                              self.user,
                                              self.content_type,
                                              self.object_id,
        )

    @property
    def cached_user(self):
        return Memcached_helper.get_object_through_cache(User, self.user_id)


post_save.connect(incr_likes_count, sender=Like)
pre_delete.connect(decr_likes_count, sender=Like)
