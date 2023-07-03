from django_hbase import models

class HBaseFollowing(models.HBaseModel):
    from_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()

    to_user_id = models.IntegerField(column_family="cf")

    class Meta:
        table_name = "twitter_following"
        row_key = ('from_user_id', 'created_at')


class HBaseFollower(models.HBaseModel):
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()

    from_user_id = models.IntegerField(column_family="cf")

    class Meta:
        table_name = "twitter_follower"
        row_key = ('to_user_id', 'created_at')