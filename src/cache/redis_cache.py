from typing import List, Union

import msgpack
import redis
from fastapi import HTTPException


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.StrictRedis.from_url(redis_url)
        self.test_redis_connection()

    def test_redis_connection(self):
        try:
            self.redis.ping()
            print('Successfully connected to Redis')
        except redis.ConnectionError as e:
            print(f'Failed to connect to Redis: {e}')
            raise HTTPException(
                status_code=500, detail=f'Failed to connect to Redis: {e}'
            )

    def get(self, key: str) -> Union[List, None]:
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return msgpack.unpackb(cached_data)
            return None
        except redis.RedisError as e:
            print(f'Redis get error: {e}')
            return None

    def set(self, key: str, data: List, ttl: int = 600):
        try:
            self.redis.setex(key, ttl, msgpack.packb(data))
        except redis.RedisError as e:
            print(f'Redis set error: {e}')
