from redis import Redis

from .settings.rq import REDIS_URL

redis_conn = Redis.from_url(REDIS_URL)
