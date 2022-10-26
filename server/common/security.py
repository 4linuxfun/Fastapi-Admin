from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..settings import settings

# to get a string like this run:
# openssl rand -hex 32


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
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = token_encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
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


def token_decode(token, secret_key=settings.SECRET_KEY, algorithm=settings.ALGORITHM):
    """
    token解密
    :param token:
    :param secret_key:
    :param algorithm:
    :return:
    """
    return jwt.decode(token, secret_key, algorithm)
