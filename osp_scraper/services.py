

from redis import Redis
from rq import Queue

from .settings.rq import REDIS_URL


redis_conn = Redis.from_url(REDIS_URL)

queue = Queue(connection=redis_conn)
