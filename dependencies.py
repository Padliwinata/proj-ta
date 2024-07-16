import typing
from typing import Dict, Any, Union
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from deta import _Base
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import jwt
from pydantic import BaseModel

from db import (
    db_log,
    db_notification,
    get_user_by_username,
    get_user_by_email, insert_new_log, insert_new_notification
)
from settings import SECRET_KEY, ALGORITHM, JWT_EXPIRED
from models import User, Payload, CustomResponse, UserDB, Event
from utils import encrypt_password, decrypt_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')
f = Fernet(SECRET_KEY)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


def authenticate_user(db: _Base, username: str, password: str) -> Union[User, None]:
    response = db.fetch([{'username': username}, {'email': username}])
    if response.count == 0:
        return None

    user = response.items[0]
    user_instance = User(**user)
    if f.decrypt(user['password']).decode('utf-8') != password:
        return None

    return user_instance


def alter_auth(username: str, password: str) -> typing.Optional[User]:
    user_by_username = get_user_by_username(username)
    user_by_email = get_user_by_email(username)
    response = any([user_by_username, user_by_email])
    if not response:
        return None

    user = user_by_email or user_by_username

    if decrypt_password(user['password']) != password:
        return None

    return User(**user)


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    to_encode.update(
        {'exp': datetime.now() - timedelta(hours=7) + timedelta(seconds=JWT_EXPIRED), 'iat': datetime.now()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    to_encode.update({'exp': datetime.now() + timedelta(days=30), 'iat': datetime.now()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_payload_from_token(access_token: str) -> Payload:
    return Payload(**jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM]))


def create_response(
        message: str,
        success: bool = False,
        status_code: int = 400,
        data: typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any], None] = None
) -> JSONResponse:
    response = CustomResponse(
        success=success,
        code=status_code,
        message=message,
        data=data
    )
    return JSONResponse(
        response.dict(),
        status_code=status_code
    )


def create_log(user: UserDB, event: Event, detail: typing.Dict[str, typing.Any], host: str) -> typing.Dict[str, typing.Any]:
    tanggal = datetime.now()
    # if host not in ['127.0.0.1', 'localhost']:
    tanggal -= timedelta(hours=7)

    data_to_store = {
        'name': user.full_name,
        'email': user.email,
        'role': user.role,
        'tanggal': tanggal.strftime('%Y-%m-%d %H:%M:%S'),
        'event': event,
        'detail': detail,
        'id_institution': user.id_institution
    }

    # db_log.put(data_to_store)
    insert_new_log(data_to_store)

    return data_to_store


