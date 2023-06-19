import subprocess
import json
from datetime import datetime
from loguru import logger
from sqlmodel import text
from utils import Channel
from config import rpc_config
from models import engine


def run_command_with_channel(job_id=None, command=None):
    """
    本地执行命令，并把任务实时输入redis中。任务结束后，日志写入数据库中
    :param job_id:任务名
    :param command: 执行的命令
    """
    with Channel(rpc_config.redis, job_id=job_id) as channel:
        logger.debug(f"job id:{job_id}")
        channel.send({'msg': '开始执行任务：'})
        channel.send({'msg': f"执行命令：{command}"})
        start_time = datetime.now()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   shell=True)
        while (status := process.poll()) is None:
            message = process.stdout.readline()
            channel.send({'msg': message})
        channel.send({'msg': '结束执行任务'})
        end_time = datetime.now()
        with engine.connect() as conn:
            sql = text(
                "INSERT INTO job_log (status,job_id,start_time,end_time,log) values (:status,:job_id,:start_time,:end_time,:log)")
            conn.execute(sql,
                         {'status': status, 'job_id': job_id, 'start_time': start_time, 'end_time': end_time,
                          'log': json.dumps(channel.msg)})
            conn.commit()
