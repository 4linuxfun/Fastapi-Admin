import redis
from loguru import logger
from typing import Dict, Any, List
from models import InventoryHost


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


def hosts_to_inventory(hosts: List[InventoryHost], private_data_dir):
    """
    转换hosts为inventory格式的数据
    :params hosts:
    :params private_data_dir:ansible-runner的环境目录，其中保存runner执行过程的所有数据
    """
    inventory = {}
    for host in hosts:
        inventory[host.name] = {
            "ansible_host": host.ansible_host,
            "ansible_port": host.ansible_port,
            "ansible_user": host.ansible_user,
        }
        if host.ansible_password:
            inventory[host.name]["ansible_password"] = host.ansible_password
        if host.ansible_ssh_private_key:
            # 私钥保存到本地文件，并指向对应路径
            inventory[host.name]["ansible_ssh_private_key_file"] = host.ansible_ssh_private_key
