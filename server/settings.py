from pydantic import BaseSettings


class APISettings(BaseSettings):
    # token加密相关参数
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # sql数据库信息
    DATABASE_URI = "mysql+pymysql://root:123456@192.168.137.129/devops"


settings = APISettings()
