import redis
from loguru import logger
from typing import Dict, Any


class Channel:
    def __init__(self, redis_config, job_id):
        self.conn = redis.Redis(**redis_config, decode_responses=True)
        self.job_id = job_id
        self.task_key = f"tasks:{self.job_id}"
        self._expire = 60

    @property
    def msg(self, ):
        return self.conn.xrange(self.task_key, '-', '+')

    @property
    def expire(self, ) -> int:
        return self._expire

    @expire.setter
    def expire(self, value: int):
        self._expire = value

    def send(self, msg: Dict[Any, Any]):
        self.conn.xadd(self.task_key, msg)

    def delete(self, ):
        self.conn.delete(self.task_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.expire(self.task_key, self._expire)
        self.close()

    def close(self, ):
        self.conn.close()
