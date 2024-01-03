from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Integer, create_engine, Session
from sqlalchemy.dialects import mysql
from config import rpc_config


engine = create_engine(rpc_config.apscheduler_job_store, pool_size=5, max_overflow=10, pool_timeout=30,
                       pool_pre_ping=True)
# SQLModel.metadata.create_all(engine)
