import subprocess
import json
from loguru import logger
from utils import Channel
from config import rpc_config
from models import session, TaskLog


def subprocess_with_channel(task_id=None, command=None):
    """
    本地执行命令，并把任务实时输入redis中。任务结束后，日志写入数据库中
    """
    with Channel(rpc_config.redis, task_id=task_id) as channel:
        logger.debug(f"task is:{task_id}")
        channel.send({'msg': '开始执行任务：'})
        channel.send({'msg': f"执行命令：{command}"})
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   shell=True)
        while process.poll() is None:
            message = process.stdout.readline()
            channel.send({'msg': message})
        channel.send({'msg': '结束执行任务'})
        task_log = TaskLog(task_id=task_id, status=process.returncode, cmd=command, type=0,
                           stdout=json.dumps(channel.msg))
        session.add(task_log)
        session.commit()
