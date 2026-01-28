import yaml
import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import casbin_sqlalchemy_adapter
import casbin
from sqlmodel import create_engine


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    casbin_model_path: str = Field("model.conf", env="CASBIN_MODEL_PATH")
    # 资产前缀
    asset_prefix: str = Field("JS", env="ASSET_PREFIX")
    # 上传目录
    upload_dir: str = Field("static/upload", env="UPLOAD_DIR")
    #  白名单
    no_verify_url: list = Field(
        ["/", "/api/login", "/api/captcha"], env="NO_VERIFY_URL"
    )
    mysql_host: str = Field(..., env="MYSQL_HOST")
    mysql_port: int = Field(3306, env="MYSQL_PORT")
    mysql_user: str = Field(..., env="MYSQL_USER")
    mysql_password: str = Field(..., env="MYSQL_PASSWORD")
    mysql_db: str = Field(..., env="MYSQL_DB")

    @property
    def database_uri(self) -> str:
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"


settings = Settings()

engine = create_engine(
    str(settings.database_uri),
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
)
adapter = casbin_sqlalchemy_adapter.Adapter(engine)
casbin_enforcer = casbin.Enforcer(settings.casbin_model_path, adapter)
