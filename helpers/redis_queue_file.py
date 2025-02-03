import sys

from typing import Callable
from rq import Queue, Retry

import redis

from api.config import config



class RedisQueue():
    def __init__(self):
        self.queue = Queue(connection=redis.StrictRedis(
            host=config.REDIS_URI, port=config.REDIS_PORT, db=0, decode_responses=True
        ))

    def enqueue(self, function: Callable, *args, **kwargs):
        self.queue.enqueue(function, *args, **kwargs, retry=Retry(max=sys.maxsize, interval=30))
