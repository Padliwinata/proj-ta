import json
from typing import Annotated, Dict, Any

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import SecretStr

from models import RegisterForm, Response, User, Refresh, ResponseDev
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


def get_user(access_token: str = Depends(oauth2_scheme)) -> User | None:
    try:
        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        user = db_user.fetch({'username': access_payload['sub']})
        if user.count == 0:
            return None
        user_data: User = user.items[0]
        return user_data
    except JWTError:
        return None


@app.post('/register')
async def register(data: RegisterForm) -> Response:
    encrypted_password = data.password.get_secret_value().encode('utf-8')
    data.password = SecretStr(f.encrypt(encrypted_password).decode('utf-8'))
    new_user = User(**data.dict())
    new_user.password = data.password
    db_user.put(**json.loads(new_user.json()))
    payload = {'username': data.username}
    return Response(
        success=True,
        code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=payload
    )


@app.post("/auth", response_model=ResponseDev)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> ResponseDev:
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        return ResponseDev(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="User not found",
            data=None,
            access_token=None
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
        resp = ResponseDev(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data,
            access_token=data['access_token']
        )
        return resp
    else:
        return ResponseDev(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data,
            access_token=None
        )


@app.get("/auth")
async def check(user: Dict[str, Any] = Depends(get_user)) -> Response:
    # if x_token is None:
    #     return Response(
    #         success=False,
    #         code=status.HTTP_401_UNAUTHORIZED,
    #         message="Credential not exist",
    #         data={
    #             'headers': {'WWW-Authenticate': "Bearer"}
    #         }
    #     )
    try:
        # payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)

        return Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=user
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
async def refresh(refresh_token: Refresh, access_token: str = Depends(oauth2_scheme)) -> Response:
    try:
        refresh_payload = jwt.decode(refresh_token.refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)

        if refresh_payload['iat'] == access_payload['iat']:
            data = {'sub': access_payload['sub'], 'role': access_payload['role']}
            access_token = create_access_token(data)
            new_refresh_token = create_refresh_token(data)

            data = TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            ).dict()
            return Response(
                success=True,
                code=status.HTTP_200_OK,
                message="Authenticated",
                data=data
            )
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Token issued time invalid",
            data=None
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


@app.post("/account")
async def register_another_account(data: User) -> Response:
    parsed_data = data.dict()
    if data.password:
        parsed_data['password'] = data.password.get_secret_value()

    registered_user = db_user.fetch(parsed_data)

    if registered_user.count != 0:
        return Response(
            success=False,
            code=status.HTTP_400_BAD_REQUEST,
            message="Username or email already registered",
            data=None
        )

    db_user.put(**parsed_data)
    del parsed_data['password']

    return Response(
        success=True,
        code=status.HTTP_201_CREATED,
        message="User created",
        data=parsed_data
    )






