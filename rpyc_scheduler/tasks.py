import subprocess
import json
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
from sqlmodel import text
from utils import Channel
from config import rpc_config
from models import engine


def local_executor(job_id, host, command):
    with Channel(rpc_config.redis, job_id=f"{job_id}:{host}") as channel:
        start_time = datetime.now()
        channel.send({'msg': '开始执行任务：'})
        channel.send({'msg': f"执行命令：{command}"})
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   shell=True)
        while (status := process.poll()) is None:
            message = process.stdout.readline()
            channel.send({'msg': message})
        channel.send({'msg': '结束执行任务'})
        end_time = datetime.now()
    return status, end_time - start_time, channel.msg


def host_executor(job_id, host, command):
    pass


def run_command_with_channel(job_id=None, targets: List[str] = None, command=None):
    """
    本地执行命令，并把任务实时输入redis中。任务结束后，日志写入数据库中
    :param job_id:任务名
    :param targets: 主机列表
    :param command: 执行的命令
    """
    run_logs: Dict[str, Dict[str, Any]] = {}
    remote_host: List[str] = []
    for host in targets:
        if host == 'localhost':
            status, duration, log = local_executor(job_id, host, command)
            run_logs[host] = {'status': status,
                              'duration': 0,
                              'log': log}
        else:
            remote_host.append(host)

    with engine.connect() as conn:
        sql = text(
            "INSERT INTO job_log (status,job_id,log) values (:status,:job_id,:log)")
        conn.execute(sql,
                     {'status': status, 'job_id': job_id,
                      'log': json.dumps(run_logs)})
        conn.commit()
