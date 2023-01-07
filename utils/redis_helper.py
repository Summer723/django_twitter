from tweets.models import Tweet
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from django.conf import settings


class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()
        serialized_list = []
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        # *[1 2 3] => 1,2,3
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)


    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()

        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            lst = []
            for data in serialized_list:
                lst.append(DjangoModelSerializer.deserialize(data))
            return lst

        cls._load_objects_to_cache(key, queryset)
        return list(queryset)


    @classmethod
    def push_objects(cls, key, obj, queryset):
        conn = RedisClient.get_connection()

        if not conn.exists(key):
            cls._load_objects_to_cache(key, queryset)
            return

        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)

    @classmethod
    def get_count_key(cls, obj, attr):
        return "{}.{}:{}".format(obj.__class__.__name__, attr, obj.id)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)

        count = conn.get(key)

        if conn is not None:
            return int(count)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        return count

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if conn.exists(key):
            return conn.incr(key)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return count

    @classmethod
    def decr_count(cls, obj, attr):
        key = cls.get_count_key(obj, attr)
        conn = RedisClient.get_connection()

        if conn.exists(key):
            return conn.decr(key)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return count


