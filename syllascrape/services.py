

from redis import Redis

from . import settings


redis_conn = Redis(settings.BROKER_HOST)
