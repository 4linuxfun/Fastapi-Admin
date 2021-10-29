from sqlmodel import Session, create_engine

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234567890@192.168.137.129/simple_sam"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
