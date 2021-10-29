from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(data):
    """
    生成token
    :param data:
    :return:
    """
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = token_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def token_encode(to_encode, secret_key, algorithm):
    """
    token加密
    :param to_encode:
    :param secret_key:
    :param algorithm:
    :return:
    """
    return jwt.encode(to_encode, secret_key, algorithm)


def token_decode(token, secret_key=SECRET_KEY, algorithm=ALGORITHM):
    """
    token解密
    :param token:
    :param secret_key:
    :param algorithm:
    :return:
    """
    return jwt.decode(token, secret_key, algorithm)
