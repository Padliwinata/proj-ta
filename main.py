import io
import json
import requests
from typing import Annotated, Union, List
from datetime import datetime

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, status, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import SecretStr, AnyUrl

from dependencies import authenticate_user, create_refresh_token, create_access_token, TokenResponse, get_payload_from_token, create_response
from db import db_user, db_institution, db_log, db_point, db_proof, drive
from exceptions import DependencyException
from models import RegisterForm, Response, User, Refresh, ResponseDev, AddUser, Institution, Log, ProofMeta, Point, Proof, UserDB, FileMeta
from settings import SECRET_KEY, ALGORITHM, DEVELOPMENT
from seeder import seed, delete_db

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


def get_user(access_token: str = Depends(oauth2_scheme)) -> Union[UserDB, None]:
    if not access_token:
        response_error = Response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized",
            data=None
        )
        raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())
    try:
        payload = get_payload_from_token(access_token)
    except JWTError:
        response_error = Response(
            success=False,
            code=status.HTTP_400_BAD_REQUEST,
            message="Invalid Token",
            data=None
        )
        raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())

    response = db_user.fetch({'username': payload.sub})
    if response.count == 0:
        response_error = Response(
            success=False,
            code=status.HTTP_400_BAD_REQUEST,
            message="Invalid Token",
            data=None
        )
        raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())

    user = response.items[0]
    return UserDB(**user)


@app.exception_handler(DependencyException)
async def custom_handler(request: Request, exc: DependencyException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail_info
    )


@app.post('/register', tags=['General', 'Auth'])
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

    email_request_header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Postmark-Server-Token': '57999240-f933-4e5f-a308-8eea7b3014d2'
    }

    email_request_body = {
        "From": "noreply@deltaharmonimandiri.com",
        "To": new_user.email,
        "HtmlBody": "<b>Example</b>",
        "TextBody": "Example",

    }

    res = requests.post("https://api.postmarkapp.com/email", headers=email_request_header, json=email_request_body)
    payload['confirm'] = res.json()

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


@app.post("/auth", tags=['General', 'Auth'])
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

    log_data = Log(name=form_data.username, email=user.email, role=user.role, tanggal=datetime.now().strftime('%-d %B %Y, %H:%M'), id_institution=user.id_institution)
    log_data_json = log_data.json()
    log_data_dict = json.loads(log_data_json)

    db_log.put(log_data_dict)

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


@app.get("/auth", tags=['General'])
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


@app.put("/auth", tags=['General'])
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


@app.post("/account", tags=['Admin'])
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


@app.post('/document_1', include_in_schema=False)
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


@app.delete("/test", include_in_schema=False)
async def delete_test_data() -> Response:
    data = db_user.fetch(test_data)
    db_user.delete(data.items[0]['key'])

    return Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Successfully deleted",
        data=None
    )


@app.get("/admin", tags=['Super Admin'])
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


@app.get("/staff", include_in_schema=False)
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


@app.get("/log", tags=['Admin'])
async def get_login_log(user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})

    id_institution = user.get_institution()['key']

    log_data = db_log.fetch([
        {'role': 'staff', 'id_institution': id_institution},
        {'role': 'reviewer', 'id_institution': id_institution}
    ])

    if log_data.count == 0:
        return create_response(
            message="Empty Data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    final_data = []
    for data in log_data.items:
        user_data = Log(**data)
        final_data.append({
            'nama': user_data.name,
            'email': user_data.email,
            'role': user_data.role,
            'tanggal': user_data.tanggal
        })

    return create_response("Fetch Data Success", True, status.HTTP_200_OK, data=final_data)


@app.post("/proof")
async def upload_proof_point(request: Request,
                             metadata: ProofMeta = Depends(),
                             user: UserDB = Depends(get_user),
                             file: UploadFile = File(...)) -> JSONResponse:

    if user.role != 'admin':
        return create_response(
            message="Forbidden Access",
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )

    content = await file.read()
    filename = f"{user.get_institution()['key']}_{metadata.bab}_{metadata.sub_bab.replace('.', '')}_{metadata.point}.pdf"

    drive.put(filename, content)

    new_proof = Proof(
        id_user=user.key,
        url=f"{request.url.hostname}/file/{filename}",
        file_name=filename
    )

    db_proof.put(new_proof.dict())

    new_point = Point(
        bab=metadata.bab,
        sub_bab=metadata.sub_bab,
        proof=new_proof,
        point=metadata.point
    )

    db_point.put(json.loads(new_point.json()))

    data = json.loads(new_point.json())

    if not file.filename:
        return create_response(
            message="Failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )

    return create_response(
        message=filename,
        status_code=status.HTTP_200_OK,
        success=True,
        data=data
    )


@app.post("/proofs", include_in_schema=False)
async def upload_proofs_point(request: Request,
                              metadata: ProofMeta = Depends(),
                              user: UserDB = Depends(get_user),
                              file: List[UploadFile] = File(...)) -> JSONResponse:

    # content = await file.read()
    filename = f"{user.get_institution()['key']}_{metadata.bab}_{metadata.sub_bab.replace('.', '')}_{metadata.point}.pdf"

    # drive.put(filename, content)

    # data = {
    #     'id_user': user.key,
    #     'url': f"{request.url}/{filename}",
    #     'file_name': filename,
    #     'length': len(file)
    # }

    new_proof = Proof(
        id_user=user.key,
        url=f"{request.url.hostname}/file/{filename}",
        file_name=filename
    )

    new_point = Point(
        bab=metadata.bab,
        sub_bab=metadata.sub_bab,
        proof=new_proof,
        point=metadata.point
    )

    data = json.loads(new_point.json())
    data['length'] = len(file)

    # if not file.filename:
    #     return create_response(
    #         message="Failed",
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         success=False
    #     )

    return create_response(
        message=filename,
        status_code=status.HTTP_200_OK,
        success=True,
        data=data
    )


@app.get("/assessment")
async def get_answers(user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
        return create_response(
            message="Forbidden Access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )


@app.get("/seed", tags=['Testing'])
async def seed_database() -> JSONResponse:
    seed()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@app.get("/delete", tags=['Testing'])
async def delete_database() -> JSONResponse:
    delete_db()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@app.get("/file/{filename}", tags=["General"])
async def get_file(filename: str) -> StreamingResponse:
    response = drive.get(filename)
    content = response.read()

    file_like = io.BytesIO(content)

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}.pdf"'
    }
    return StreamingResponse(file_like, headers=headers)



