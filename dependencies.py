from typing import Annotated
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from deta import _Base
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from settings import SECRET_KEY, ALGORITHM
from db import db_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
f = Fernet(SECRET_KEY)


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(db: _Base, username: str, password: str):
    encrypted_password = f.encrypt(password.encode('utf-8'))
    response = db.fetch({'username': username, 'password': encrypted_password})
    if response.count == 0:
        return False
    else:
        user = response.items[0]
        return user


def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.now() + timedelta(minutes=15)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




