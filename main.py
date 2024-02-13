import json
from typing import Annotated, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Header

from models import RegisterForm, Response, User
from dependencies import *

app = FastAPI()


@app.post('/register')
async def register(data: RegisterForm):
    data.password = f.encrypt(data.password.get_secret_value().encode('utf-8')).decode('utf-8')
    new_user = User(**data.dict())
    new_user.password = data.password
    db_user.put(new_user.dict())
    payload = {'username': data.username}
    return Response(
        success=True,
        code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=payload
    )


@app.post("/auth")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="User not found"
        )

    data = {'sub': form_data.username}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    ).dict()
    return Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Authenticated",
        data=data
    )


@app.get("/auth")
async def check(x_token: Optional[str] = Header(None)):
    if x_token is None:
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Credential not exist",
            data={
                'headers': {'WWW-Authenticate': "Bearer"}
            }
        )
    try:
        payload = jwt.decode(x_token, SECRET_KEY, algorithms=ALGORITHM)
        return Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=payload
        )
    except JWTError:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )


