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



class RedisToken():
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host=config.REDIS_URI, port=config.REDIS_PORT, db=0, decode_responses=True
        )
        
    def set_token(self, token: str, value: str, expiry: int):
        self.redis_client.setex(token, expiry, value)

    def get_token(self, token: str):
        return self.redis_client.get(token)
    
    def delete_token(self, token: str):
        self.redis_client.delete(token)
    
    def check_token(self, token: str):
        return self.redis_client.exists(token)
