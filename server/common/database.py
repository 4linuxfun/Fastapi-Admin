import redis.asyncio as redis
from sqlmodel import create_engine, SQLModel, Session, select
from ..settings import engine


def init_db():
    """
    数据库初始化
    :return:
    """
    SQLModel.metadata.create_all(engine)


# 数据库的dependency，用于每次请求都需要创建db连接时使用
def get_session():
    with Session(engine) as session:
        yield session


def get_or_create(session: Session, model, **kwargs):
    """
    检查表中是否存在对象，如果不存在就创建
    :param session:
    :param model: 表模型
    :param kwargs: 表模型参数
    :return:
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


async def get_redis():
    redis_conn = redis.Redis(**settings.redis_config)
    try:
        yield redis_conn
    finally:
        await redis_conn.close()
