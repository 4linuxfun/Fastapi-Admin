import os.path
import subprocess
import json
import ansible_runner
from pathlib import Path
from pydantic import parse_obj_as
from typing import List, Dict, Any, Union
from datetime import datetime
from loguru import logger
from sqlmodel import text
from utils import Channel, hosts_to_inventory
from config import rpc_config
from models import engine, InventoryHost


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
    return status, (end_time - start_time).total_seconds(), channel.msg


def ansible_task(job_id, targets, ansible_args):
    private_data_dir = Path(f'/tmp/ansible/{job_id}')
    if not private_data_dir.exists():
        private_data_dir.mkdir(parents=True)
    logger.debug(f'job id:{job_id},task hosts:{targets},ansible_args:{ansible_args}')
    hosts: List[InventoryHost] = []
    with engine.connect() as conn:
        sql = text(
            "select id,name,ansible_host,ansible_port,ansible_user,ansible_password,ansible_ssh_private_key from host where id in :targets").bindparams(
            targets=targets)
        result = conn.execute(sql).fetchall()
        logger.debug(result)
        for row in result:
            hosts.append(
                InventoryHost(id=row[0], name=row[1], ansible_host=row[2], ansible_port=row[3], ansible_user=row[4],
                              ansible_password=row[5], ansible_ssh_private_key=row[6]))
    ansible_inventory = hosts_to_inventory(hosts, private_data_dir)
    logger.debug(ansible_inventory)
    runner = ansible_runner.run(private_data_dir=str(private_data_dir), inventory=ansible_inventory,
                                host_pattern='all',
                                **ansible_args)


def run_command_with_channel(job_id=None, targets: List[str] = None, command=None):
    """
    本地执行命令，并把任务实时输入redis中。任务结束后，日志写入数据库中
    :param job_id:任务名
    :param targets: 主机列表
    :param command: 执行的命令
    """
    run_logs: Dict[str, Dict[str, Any]] = {}
    remote_host: List[str] = []
    start_time = datetime.now()
    for host in targets:
        if host == 'localhost':
            status, duration, log = local_executor(job_id, host, command)
            run_logs[host] = {'status': status,
                              'duration': 0,
                              'log': log}
        else:
            remote_host.append(host)
    end_time = datetime.now()
    with engine.connect() as conn:
        sql = text(
            "INSERT INTO job_log (status,job_id,start_time,end_time,log) values (:status,:job_id,:start_time,:end_time,:log)")
        conn.execute(sql,
                     {'status': status, 'job_id': job_id,
                      'start_time': start_time,
                      'end_time': end_time,
                      'log': json.dumps(run_logs)})
        conn.commit()
