

from redis import Redis

from . import settings


redis_conn = Redis.from_url(settings.REDIS_URL)
