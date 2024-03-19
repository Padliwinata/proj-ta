import json
from typing import Annotated, Union, Dict, Any, Tuple

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import SecretStr

from models import RegisterForm, Response, User, Refresh, ResponseDev, AddUser, Institution, Payload
from dependencies import authenticate_user, create_refresh_token, create_access_token, TokenResponse, get_payload_from_token, create_response
from db import db_user, db_institution, drive
from settings import SECRET_KEY, ALGORITHM, DEVELOPMENT

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth', auto_error=False)
f = Fernet(SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

test_data = {
    'username': 'testing_username',
    'email': 'testing@gmail.com'
}


def get_user(access_token: str = Depends(oauth2_scheme)) -> Union[User, None]:
    if not access_token:
        return None
    try:
        payload = get_payload_from_token(access_token)
    except JWTError:
        return None

    response = db_user.fetch({'username': payload.sub})
    if response.count == 0:
        return None

    user = response.items[0]
    return User(**user)


@app.post('/register')
async def register(data: RegisterForm) -> JSONResponse:
    encrypted_password = data.password.get_secret_value().encode('utf-8')
    data.password = SecretStr(f.encrypt(encrypted_password).decode('utf-8'))
    new_data = data.dict()

    institution_data = dict()
    institution_data['name'] = new_data['institution_name']
    institution_data['address'] = new_data['institution_address']
    institution_data['phone'] = new_data['institution_phone']
    institution_data['email'] = new_data['institution_email']
    new_institution = Institution(**institution_data)
    stored_institution = db_institution.put(json.loads(new_institution.json()))

    user_data = dict()
    user_data['username'] = new_data['username']
    user_data['full_name'] = new_data['full_name']
    user_data['email'] = new_data['email']
    user_data['password'] = new_data['password']

    user_data['is_active'] = False
    user_data['id_institution'] = stored_institution['key']
    new_user = User(**user_data)
    new_user.password = data.password.get_secret_value().encode('utf-8')
    db_user.put(json.loads(new_user.json()))

    payload = {
        'user': data.username,
        'institution': institution_data['name']
    }

    response = Response(
        success=True,
        code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=payload
    )
    return JSONResponse(
        response.dict(),
        status_code=status.HTTP_201_CREATED
    )


@app.post("/auth")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JSONResponse:
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        response = ResponseDev(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="User not found",
            data=None,
            access_token=None
        )
        return JSONResponse(
            response.dict(),
            status_code=status.HTTP_401_UNAUTHORIZED
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
        resp_dev = ResponseDev(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data,
            access_token=data['access_token']
        )
        return JSONResponse(
            resp_dev.dict(),
            status_code=status.HTTP_200_OK
        )
    else:
        resp = Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data
        )
        return JSONResponse(
            resp.dict(),
            status_code=status.HTTP_200_OK
        )


@app.get("/auth")
async def check(access_token: str = Depends(oauth2_scheme)) -> JSONResponse:
    try:
        if not access_token:
            response = Response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Credentials not found",
                data=None
            )
            return JSONResponse(
                response.dict(),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        payload = get_payload_from_token(access_token)
        res = db_user.fetch({'username': payload.sub})
        if res.count == 0:
            response = Response(
                success=False,
                code=status.HTTP_404_NOT_FOUND,
                message="User not found",
                data=None
            )

            return JSONResponse(
                response.dict(),
                status_code=status.HTTP_404_NOT_FOUND
            )
        data = res.items[0]
        data['payload'] = payload.dict()

        response = Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data
        )
        return JSONResponse(
            response.dict(),
            status_code=status.HTTP_200_OK
        )
    except JWTError:
        response = Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )
        return JSONResponse(
            response.dict(),
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@app.put("/auth")
async def refresh(refresh_token: Refresh, access_token: str = Depends(oauth2_scheme)) -> Response:
    try:
        refresh_payload = get_payload_from_token(refresh_token.refresh_token)
        access_payload = get_payload_from_token(access_token)

        if refresh_payload.iat == access_payload.iat:
            data = {'sub': access_payload.sub, 'role': access_payload.role}
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
async def register_staff(data: AddUser, user: User = Depends(get_user)) -> JSONResponse:
    if not user:
        return create_response("Credentials Not Found", False, status.HTTP_401_UNAUTHORIZED)

    parsed_data = data.dict()
    if data.password:
        parsed_data['password'] = data.password.get_secret_value()

    registered_user = db_user.fetch(parsed_data)

    if registered_user.count != 0:
        return create_response("User Already Exist", False, status.HTTP_400_BAD_REQUEST)

    encoded_password = parsed_data['password'].encode('utf-8')
    encrypted_password = f.encrypt(encoded_password).decode('utf-8')

    parsed_data['password'] = encrypted_password
    parsed_data['is_active'] = False
    parsed_data['id_institution'] = user.get_institution()['key']

    db_user.put(parsed_data)
    del parsed_data['password']

    return create_response("User Created", True, status.HTTP_201_CREATED, parsed_data)


@app.post('/document_1')
async def upload_document_1(access_token: str = Depends(oauth2_scheme), file: UploadFile = File(...)) -> Response:
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError:
        return Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )

    content = await file.read()
    drive.put(f'{payload["sub"]}_1.pdf', content)

    return Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Successfully stored",
        data={
            'filename': f'{payload["sub"]}_1.pdf',
            'issuer': f'{payload["sub"]}'
        }
    )


@app.delete("/test")
async def delete_test_data() -> Response:
    data = db_user.fetch(test_data)
    db_user.delete(data.items[0]['key'])

    return Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Successfully deleted",
        data=None
    )


@app.get("/admin")
async def get_admin_list(user: User = Depends(get_user)) -> JSONResponse:
    if not user:
        return create_response("Credentials Not Found", False, status.HTTP_401_UNAUTHORIZED)

    if user.role != 'super admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})

    fetch_data = db_user.fetch({'role': 'admin'})
    if fetch_data.count == 0:
        response = Response(
            success=True,
            code=status.HTTP_200_OK,
            message="Fetch Data Success",
            data=[]
        )
        return JSONResponse(
            response.dict(),
            status_code=status.HTTP_200_OK
        )

    final_data = []
    for data in fetch_data.items:
        user = User(**data)
        final_data.append({
            'institusi': user.get_institution(),
            'id': data['key'],
            'email': data['email'],
            'is_active': data['is_active']
        })

    response = Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Fetch Data Success",
        data=final_data
    )

    return JSONResponse(
        response.dict(),
        status_code=status.HTTP_200_OK
    )


@app.get("/staff")
async def get_staff(user: User = Depends(get_user)) -> JSONResponse:
    if not user:
        return create_response("Credentials Not Found", False, status.HTTP_401_UNAUTHORIZED)

    id_institution = user.get_institution()['key']

    fetch_response = db_user.fetch(
        {'role': 'staff', 'id_institution': id_institution},
        {'role': 'reviewer', 'id_institution': id_institution}
    )

    if fetch_response.count == 0:
        return create_response(
            message="Empty Data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    # final_data = []
    # for data in fetch_response.items:







