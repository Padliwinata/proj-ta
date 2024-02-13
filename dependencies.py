from typing import Annotated
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from deta import _Base
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from settings import SECRET_KEY, ALGORITHM
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')
f = Fernet(SECRET_KEY)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


def authenticate_user(db: _Base, username: str, password: str):
    response = db.fetch({'username': username})
    if response.count == 0:
        return None

    user = response.items[0]
    user_instance = User(**user)
    if f.decrypt(user['password']).decode('utf-8') == password:
        return user_instance


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.now() + timedelta(minutes=15), 'iat': datetime.now()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.now() + timedelta(days=30), 'iat': datetime.now()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




