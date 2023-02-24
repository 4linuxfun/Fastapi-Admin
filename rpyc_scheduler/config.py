from pydantic import BaseSettings


class RpcConfig(BaseSettings):
    # apscheduler指定job store和excutors
    apscheduler_job_store = 'mysql+pymysql://root:123456@192.168.137.129/devops'
    redis = {'host': '192.168.137.129', 'password':'seraphim','port': 6379, 'health_check_interval': 30}
    rpc_port = 18861


rpc_config = RpcConfig()
