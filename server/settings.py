import yaml
import os
from pathlib import Path
import casbin_sqlalchemy_adapter
import casbin
from sqlmodel import create_engine

# 获取环境变量，默认为 development
env = os.getenv('ENV', 'development')
config_path = Path(__file__).parent.parent / 'config' / f'{env}.yaml'

# 读取配置文件
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    settings = config['server']

engine = create_engine(
    str(settings['database_uri']), 
    pool_size=5, 
    max_overflow=10, 
    pool_timeout=30, 
    pool_pre_ping=True
)
adapter = casbin_sqlalchemy_adapter.Adapter(engine)
casbin_enforcer = casbin.Enforcer(settings['casbin_model_path'], adapter)
