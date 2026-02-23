import os


def get_redis_client():
    redis_url = os.getenv("REDIS_CACHE_URL") or os.getenv("CELERY_BROKER_URL")
    if not redis_url:
        return None
    try:
        import redis
    except ModuleNotFoundError:
        return None
    return redis.Redis.from_url(redis_url, decode_responses=True)


def build_cache_key(shop_id, placement, seed_sku, version):
    return f"recommendations:{shop_id}:{placement}:{seed_sku}:{version}"


def get_cached_candidates(cache_key):
    client = get_redis_client()
    if not client:
        return None
    return client.get(cache_key)


def set_cached_candidates(cache_key, payload):
    client = get_redis_client()
    if not client:
        return False
    client.set(cache_key, payload)
    return True


def delete_cache_keys(cache_keys):
    client = get_redis_client()
    if not client or not cache_keys:
        return 0
    if isinstance(cache_keys, str):
        cache_keys = [cache_keys]
    return client.delete(*cache_keys)
