import json
from typing import Annotated, Optional

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError

from models import RegisterForm, Response, User, Refresh
from dependencies import authenticate_user, create_refresh_token, create_access_token, TokenResponse
from db import db_user
from settings import SECRET_KEY, ALGORITHM, DEVELOPMENT

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')
f = Fernet(SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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

    data = {'sub': form_data.username, 'role': user.role}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    ).dict()
    if DEVELOPMENT:
        resp = Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data
        ).dict()
        resp['access_token'] = resp['data']['access_token']
        return resp
    else:
        return Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data
        )


@app.get("/auth")
async def check(x_token: str = Depends(oauth2_scheme)):
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
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )


@app.put("/auth")
async def refresh(refresh_token: Refresh, access_token: str = Depends(oauth2_scheme)):
    try:
        refresh_payload = jwt.decode(refresh_token.refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)

        if refresh_payload['iat'] == access_payload['iat']:
            data = {'sub': access_payload['sub'], 'role': access_payload['role']}
            access_token = create_access_token(data)
            refresh_token = create_refresh_token(data)

            data = TokenResponse(
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
        else:
            return Response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Token issued time invalid"
            )

    except JWTError:
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )



