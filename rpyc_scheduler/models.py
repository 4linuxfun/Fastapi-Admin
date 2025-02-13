from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Integer, create_engine, Session
from sqlalchemy.dialects import mysql
from .config import rpc_config
from sqlmodel import SQLModel
from typing import Union

engine = create_engine(str(rpc_config['apscheduler_job_store']), pool_size=5, max_overflow=10, pool_timeout=30,
                       pool_pre_ping=True)


# SQLModel.metadata.create_all(engine)

class InventoryHost(SQLModel):
    """
    主机资产涉及的参数
    """
    name: str
    ansible_host: str
    ansible_port: int = 22
    ansible_user: str
    ansible_password: Union[str, None] = None
    ansible_ssh_private_key: Union[str, None] = None


class AnsibleInventory(SQLModel):
    pass
