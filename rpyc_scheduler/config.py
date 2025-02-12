import yaml
import os
from pathlib import Path

# 获取环境变量，默认为 development
env = os.getenv('ENV', 'development')
config_path = Path(__file__).parent.parent / 'config' / f'{env}.yaml'

# 初始化配置变量
rpc_config = {}

# 读取配置文件
def load_config():
    global rpc_config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        rpc_config.update(config['scheduler'])

# 加载配置
load_config()
