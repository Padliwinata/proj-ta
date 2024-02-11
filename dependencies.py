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

app = FastAPI()
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


@app.post("/auth")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = {'sub': form_data.username}
    access_token = create_token(data)
    return Token(access_token=access_token, token_type="bearer")

