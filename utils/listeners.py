def invalidate_object_cache(sender, instance, **kwargs):
    from utils.memcached_helper import Memcached_helper
    Memcached_helper.invalidate_cached_object(sender, instance.id)