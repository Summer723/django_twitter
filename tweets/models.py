from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now



# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='The user who created this tweet.',
    )
    content = models.CharField(max_length=255)
    # auto_now_add means it will return the time it created
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600


    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'
