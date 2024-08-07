import io
import json
from datetime import datetime, timedelta
from typing import Annotated, Union, List

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, status, File, UploadFile, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError
import pandas as pd
from pydantic import SecretStr

from db import (
    db_user,
    db_institution,
    db_log,
    db_point,
    db_proof,
    drive,
    db_assessment,
    db_report,
    db_notification
)
from dependencies import (
    authenticate_user,
    create_refresh_token,
    create_access_token,
    TokenResponse,
    get_payload_from_token,
    create_response,
    create_log,
    create_notification
)
from exceptions import DependencyException
from models import (
    RegisterForm,
    CustomResponse,
    User,
    Refresh,
    CustomResponseDev,
    AddUser,
    Institution,
    Log,
    ProofMeta,
    Point,
    Proof,
    UserDB,
    AssessmentDB,
    AssessmentEval,
    Report,
    ResetPassword,
    Event, ReportInput
)
from seeder import seed, delete_db, seed_assessment
from settings import SECRET_KEY, MAX_FILE_SIZE, DEVELOPMENT

from utils import encrypt_password

# import pymysql.cursors

app = FastAPI(
    title="FDP",
    version="1.0.2"
)
router = APIRouter(prefix='/api')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth', auto_error=False)
f = Fernet(SECRET_KEY)

request_origins = [
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
    'https://devta-1-j8022502.deta.app'
    'https://fe-fraud.vercel.app',
    'https://www.frauddeterrence.online',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

test_data = {
    'username': 'testing_username',
    'email': 'testing@gmail.com'
}

bab = [
    '1.1',
    '1.2',
    '2.1',
    '2.2',
    '3.1',
    '3.2',
    '4.1',
    '4.2',
    '5.1',
    '6.1'
]

question_number = [10, 10, 10, 10, 8, 7, 7, 8, 15, 15]


def get_user(access_token: str = Depends(oauth2_scheme)) -> Union[UserDB, None]:
    if not access_token:
        response_error = CustomResponse(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized",
            data=None
        )
        raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())
    try:
        payload = get_payload_from_token(access_token)
    except JWTError:
        response_error = CustomResponse(
            success=False,
            code=status.HTTP_400_BAD_REQUEST,
            message="Invalid Token",
            data=None
        )
        raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())

    response = db_user.fetch({'username': payload.sub})
    # user_data = get_user_by_username(payload.sub)
    # if response.count == 0:
    #     response_error = CustomResponse(
    #         success=False,
    #         code=status.HTTP_400_BAD_REQUEST,
    #         message="Invalid Token",
    #         data=None
    #     )
    #     raise DependencyException(status_code=status.HTTP_401_UNAUTHORIZED, detail_info=response_error.dict())

    user = response.items[0]
    return UserDB(**user)


@app.exception_handler(DependencyException)
async def custom_handler(request: Request, exc: DependencyException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail_info
    )


@router.post('/register', tags=['Auth'])
async def register(data: RegisterForm) -> JSONResponse:
    existing_data_user = db_user.fetch([{'username': data.username}, {'email': data.email}, {'phone': data.phone}])
    existing_data_institution = db_institution.fetch([{'phone': data.institution_phone}, {'email': data.institution_email}])

    existing_data = existing_data_user.count + existing_data_institution.count

    if existing_data > 0:
        return create_response(
            message="Username or email already exist"
        )

    data.password = SecretStr(encrypt_password(data.password.get_secret_value()))
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
    user_data['phone'] = new_data['phone']
    user_data['email'] = new_data['email']
    user_data['password'] = new_data['password']

    user_data['is_active'] = False
    user_data['id_institution'] = stored_institution['key']
    new_user = User(**user_data)
    new_user.password = data.password.get_secret_value().encode('utf-8')
    res = db_user.put(json.loads(new_user.json()))

    # userid: str = res['key']
    # send_confirmation(userid, new_user.email, new_user.full_name)

    payload = {
        'user': data.username,
        'institution': institution_data['name']
    }

    response = CustomResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=payload
    )
    return JSONResponse(
        response.dict(),
        status_code=status.HTTP_201_CREATED
    )


@router.post("/auth", tags=['Auth'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JSONResponse:
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        response = CustomResponseDev(
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

    if not user.is_active:
        return JSONResponse(
            {'message': 'User inactive',
             'success': False},
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

    log_data = Log(name=form_data.username, event=Event.logged_in, email=user.email, role=user.role, tanggal=datetime.now().strftime('%d %B %Y, %H:%M'), id_institution=user.id_institution)
    log_data_json = log_data.json()
    log_data_dict = json.loads(log_data_json)

    db_log.put(log_data_dict)

    if DEVELOPMENT:
        resp_dev = CustomResponseDev(
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
        resp = CustomResponse(
            success=True,
            code=status.HTTP_200_OK,
            message="Authenticated",
            data=data
        )
        return JSONResponse(
            resp.dict(),
            status_code=status.HTTP_200_OK
        )


@router.get("/auth", tags=['Auth'])
async def check(access_token: str = Depends(oauth2_scheme)) -> JSONResponse:
    try:
        if not access_token:
            response = CustomResponse(
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
            response = CustomResponse(
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

        response = CustomResponse(
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
        response = CustomResponse(
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


@router.put("/auth", tags=['Auth'])
async def refresh(refresh_token: Refresh, access_token: str = Depends(oauth2_scheme)) -> CustomResponse:
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
            return CustomResponse(
                success=True,
                code=status.HTTP_200_OK,
                message="Authenticated",
                data=data
            )
        return CustomResponse(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Token issued time invalid",
            data=None
        )

    except JWTError:
        return CustomResponse(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            data={
                'headers': {'WWW-Authenticate': 'Bearer'}
            }
        )


@router.post("/account", tags=['Admin'])
async def register_staff(data: AddUser, user: User = Depends(get_user)) -> JSONResponse:
    if not user:
        return create_response("Credentials Not Found", False, status.HTTP_401_UNAUTHORIZED)

    parsed_data = data.dict()
    if isinstance(data.password, SecretStr):  # Periksa apakah password adalah SecretStr
        parsed_data['password'] = data.password.get_secret_value()

    registered_username = data.username
    registered_email = data.email

    registered_user = db_user.fetch([{'username': registered_username}, {'email': registered_email}])

    if registered_user.count != 0:
        return create_response("User Already Exist", False, status.HTTP_400_BAD_REQUEST)

    encrypted_password = encrypt_password(parsed_data['password'])

    parsed_data['password'] = encrypted_password
    parsed_data['is_active'] = False
    parsed_data['id_institution'] = user.get_institution()['key']

    db_user.put(parsed_data)
    del parsed_data['password']

    return create_response("User Created", True, status.HTTP_201_CREATED, parsed_data)


@router.patch('/alter', tags=['General - Admin'])
async def alternate_staff_status(user_key: str, user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})
    if not user_key:
        return create_response("Missing user key", False, status.HTTP_400_BAD_REQUEST)

    existing_user = db_user.get(user_key)
    db_user.update({'is_active': not existing_user['is_active']}, key=user_key)
    existing_user['is_active'] = not existing_user['is_active']

    return create_response("Success altering user status", True, status.HTTP_200_OK, existing_user)


@router.get("/admin", tags=['General - Super Admin'])
async def get_admin_list(user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'super admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})

    fetch_data = db_user.fetch({'role': 'admin'})
    if fetch_data.count == 0:
        response = CustomResponse(
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

    response = CustomResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Fetch Data Success",
        data=final_data
    )

    return JSONResponse(
        response.dict(),
        status_code=status.HTTP_200_OK
    )


@router.get("/staff", tags=['General - Admin'])
async def get_staff(user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})

    id_institution = user.get_institution()['key']

    fetch_response = db_user.fetch([
        {'role': 'staff', 'id_institution': id_institution},
        {'role': 'reviewer', 'id_institution': id_institution}
    ])

    if fetch_response.count == 0:
        return create_response(
            message="Empty Data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    final_data = []
    for user in fetch_response.items:
        parsed_user = dict(user)
        final_data.append({
            'full_name': parsed_user['full_name'],
            'email': parsed_user['email'],
            'role': parsed_user['role'],
            'status': parsed_user['is_active'],
            'key': parsed_user['key']
        })

    return create_response(
        "Success fetch data",
        True,
        status.HTTP_200_OK,
        data=final_data
    )
    # for data in fetch_response.items:


@router.get("/log", tags=['General - Admin'])
async def get_login_log(user: User = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
        return create_response("Forbidden Access", False, status.HTTP_403_FORBIDDEN, {'role': user.role})

    id_institution = user.get_institution()['key']

    log_data = db_log.fetch([
        {'role': 'staff', 'id_institution': id_institution},
        {'role': 'reviewer', 'id_institution': id_institution},
        {'role': 'admin', 'id_institution': id_institution}
    ])

    if log_data.count == 0:
        return create_response(
            message="Empty Data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    # print(log_data.items[0])
    # print(type(log_data.items[0]['tanggal']))

    final_data = []
    for data in log_data.items:
        user_data = Log(**data)
        final_data.append({
            'nama': user_data.name,
            'email': user_data.email,
            'role': user_data.role,
            'event': user_data.event,
            'tanggal': user_data.tanggal
        })

    final_data = sorted(final_data, key=lambda x: datetime.strptime(x['tanggal'], '%d %B %Y, %H:%M'), reverse=True)

    return create_response("Fetch Data Success", True, status.HTTP_200_OK, data=final_data)


@router.post("/point", tags=['Deterrence - Admin'])
async def upload_proof_point(request: Request,
                             metadata: ProofMeta = Depends(),
                             user: UserDB = Depends(get_user),
                             file: UploadFile = File(None)) -> JSONResponse:

    if user.role not in ['admin', 'staff']:
        return create_response(
            message="Forbidden Access",
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )

    content = None

    if file:
        if file.size > MAX_FILE_SIZE:
            return create_response(
                message="File Too Large",
                success=False,
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        else:
            content = await file.read()

    filename = ''
    new_proof = None
    if file:
        filename = f"{user.get_institution()['key']}_{metadata.bab}_{metadata.sub_bab.replace('.', '')}_{metadata.point}.pdf"

        new_proof = Proof(
            id_user=user.key,
            url=f"{request.url.hostname}/file/{filename}",
            file_name=filename
        )

    existing_assessment_data = db_assessment.fetch({'id_admin': user.key, 'selesai': False})

    if existing_assessment_data.count == 0:
        return create_response(
            message="Please create a new assessment",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    assessment_data = existing_assessment_data.items[0]
    assessment_data = AssessmentDB(**assessment_data)

    existing_points = db_point.fetch({'id_assessment': assessment_data.key, 'bab': metadata.bab, 'sub_bab': metadata.sub_bab, 'point': metadata.point})
    if existing_points.count > 0:
        return create_response(
            message="Point already exist",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if int(metadata.bab) > 6:
        return create_response(
            message="Invalid bab",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if metadata.sub_bab not in bab:
        return create_response(
            message="Invalid sub bab",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if new_proof:
        drive.put(filename, content)
        db_proof.put(new_proof.dict())

    new_point = Point(
        id_assessment=assessment_data.key,
        bab=metadata.bab,
        sub_bab=metadata.sub_bab,
        proof=new_proof,
        point=metadata.point,
        answer=metadata.answer,
        skor=None
    )

    res = db_point.put(json.loads(new_point.json()))

    data = json.loads(new_point.json())

    if file:
        if not file.filename:
            return create_response(
                message="Failed",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

    if existing_assessment_data.count == 0:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    if request.client:
        create_log(
            user=user,
            event=Event.submit_point,
            detail={
                'id_point': res['key'],
                'id_assessment': res['id_assessment'],
                'bab': res['bab'],
                'sub_bab': res['sub_bab']
            },
            host=request.client.host
        )

    return create_response(
        message=filename,
        status_code=status.HTTP_200_OK,
        success=True,
        data=data
    )


@router.patch('/point', tags=['Deterrence - Admin'])
async def update_assessment(request: Request,
                            metadata: ProofMeta = Depends(),
                            user: UserDB = Depends(get_user),
                            file: UploadFile = File(None)) -> JSONResponse:
    if user.role != 'admin':
        return create_response(
            message="Forbidden Access",
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )

    existing_assessment_data = db_assessment.fetch({'id_admin': user.key, 'selesai': False})
    if existing_assessment_data.count == 0:
        return create_response(
            message="No active assessment",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    assessment = AssessmentDB(**existing_assessment_data.items[0])

    # current_point = db_point.fetch({'bab': metadata.bab, 'sub_bab': metadata.sub_bab, 'point': metadata.point})
    current_point = db_point.fetch({'id_assessment': assessment.key, 'bab': metadata.bab, 'sub_bab': metadata.sub_bab, 'point': metadata.point})
    if current_point.count == 0:
        return create_response(
            message="Point not found",
            status_code=status.HTTP_404_NOT_FOUND,
            success=False
        )

    key = current_point.items[0]['key']
    res = db_point.get(key)
    actual_point = Point(**res)

    content = None
    if file:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            return create_response(
                message="File too big",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    filename = f"{user.get_institution()['key']}_{metadata.bab}_{metadata.sub_bab.replace('.', '')}_{metadata.point}.pdf"
    if file:
        drive.delete(filename)
        drive.put(filename, content)
        if not actual_point.proof:
            new_proof = Proof(
                id_user=user.key,
                url=f"{request.url.hostname}/api/actualfile/{filename}",
                file_name=filename
            )

            actual_point.proof = new_proof
            db_proof.put(new_proof.dict())

    actual_point.answer = metadata.answer
    db_point.update(actual_point.dict(), key)

    if request.client:
        create_log(
            user=user,
            event=Event.edited_point,
            detail={
                'id_point': key,
                'id_assessment': actual_point.id_assessment,
                'bab': actual_point.bab,
                'sub_bab': actual_point.sub_bab
            },
            host=request.client.host
        )

    return create_response(
        message='Update success',
        status_code=status.HTTP_200_OK,
        success=True,
        data=res
    )


@app.delete("/file/{filename}", tags=['Deterrence - Admin'])
async def delete_proof(filename: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role not in ['admin', 'staff']:
        return create_response(
            message="Forbidden Access",
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )

    existing_proof = db_proof.fetch({'file_name': filename})
    if existing_proof.count == 0:
        return create_response(
            message="Proof not found",
            status_code=status.HTTP_404_NOT_FOUND,
            success=False
        )

    actual_proof = existing_proof.items[0]
    db_proof.delete(actual_proof['key'])
    drive.delete(filename)

    existing_point = db_point.fetch({'proof.file_name': filename})
    if existing_point.count == 0:
        return create_response(
            message="Proof successfully deleted without updating point",
            status_code=status.HTTP_200_OK,
            success=True,
            data=actual_proof
        )

    actual_point = existing_point.items[0]
    actual_point['proof'] = None

    key = actual_point['key']
    del actual_point['key']

    db_point.update(actual_point, key)

    return create_response(
        message="Proof successfully deleted with updating point",
        status_code=status.HTTP_200_OK,
        success=True,
        data=actual_proof
    )


@app.get('/entitas', tags=['General'])
async def get_entitas(user: UserDB = Depends(get_user)) -> JSONResponse:
    return create_response(
        message="Get entity success",
        status_code=status.HTTP_200_OK,
        success=True,
        data=user.get_institution()
    )


@router.post("/proofs", include_in_schema=False)
async def upload_proofs_point(request: Request,
                              metadata: ProofMeta = Depends(),
                              user: UserDB = Depends(get_user),
                              file: List[UploadFile] = File(...)) -> JSONResponse:

    # content = await file.read()
    filename = f"{user.get_institution()['key']}_{metadata.bab}_{metadata.sub_bab.replace('.', '')}_{metadata.point}.pdf"

    new_proof = Proof(
        id_user=user.key,
        url=f"{request.url.hostname}/file/{filename}",
        file_name=filename
    )

    new_point = Point(
        bab=metadata.bab,
        sub_bab=metadata.sub_bab,
        proof=new_proof,
        point=metadata.point,
        skor=0
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


@router.get("/seed", tags=['Development'])
async def seed_database() -> JSONResponse:
    seed()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@router.get("/seed/assessment", tags=['Development'])
async def assessment_seeder(password: str) -> JSONResponse:
    if password != "iya":
        return create_response(
            message="Salah, jangan ngadi ngadi",
            status_code=status.HTTP_401_UNAUTHORIZED,
            success=False
        )
    seed_assessment()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@router.get("/delete", tags=['Development'])
async def delete_database() -> JSONResponse:
    delete_db()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@router.get("/file/{filename}", tags=['General'])
async def get_file(filename: str, request: Request) -> JSONResponse:
    response = drive.get(filename)
    if not response:
        return create_response(
            message="File not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        message="Fetch file success",
        success=True,
        status_code=status.HTTP_200_OK,
        data={'url': f"{request.base_url}api/actualfile/{filename}"}
    )


@router.get("/actualfile/{filename}", include_in_schema=False)
async def get_actual_file(filename: str) -> Response:
    response = drive.get(filename)
    content = response.read()

    file_like = io.BytesIO(content).getvalue()

    # headers = {
    #     'Content-Disposition': f'attachment; filename="{filename}"'
    # }
    # return StreamingResponse(file_like, headers=headers)
    return Response(content=file_like, media_type='application/pdf')


@router.get("/verify/{userid}", tags=['General - Super Admin'])
async def verify_user(userid: str) -> JSONResponse:
    resp = db_user.get(userid)
    if not resp:
        return create_response(
            message="User not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )
    reverse = not resp['is_active']
    db_user.update(
        {'is_active': reverse},
        userid
    )

    # user_data = json.loads(user.json())

    return create_response(
        message="User activated",
        success=True,
        status_code=status.HTTP_200_OK,
    )


@router.post("/assessment", tags=['Deterrence - Admin'])
async def start_assessment(user: UserDB = Depends(get_user)) -> JSONResponse:
    existing_data = db_assessment.fetch({'id_admin': user.key, 'selesai': False})
    if existing_data.count > 0:
        return create_response(
            message="Please finish last assessment first",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    current_datetime = datetime.now()
    extra_datetime = current_datetime + timedelta(hours=7)

    new_assessment = {
        'id_institution': user.id_institution,
        'id_admin': user.key,
        'id_reviewer_internal': '',
        'id_reviewer_external': '',
        'tanggal': extra_datetime.strftime('%d %B %Y, %H:%M'),
        'hasil_internal': None,
        'hasil_external': None,
        'selesai': False,
        'tanggal_nilai': None
    }

    db_assessment.put(new_assessment)

    return create_response(
        message="Start assessment success",
        success=True,
        status_code=status.HTTP_201_CREATED,
        data=new_assessment
    )


@router.get("/assessment", tags=['Deterrence - Admin'])
async def get_current_assessment(sub_bab: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    existing_assessment_data = db_assessment.fetch({'id_admin': user.key, 'selesai': False})
    if existing_assessment_data.count == 0:
        return create_response(
            message="No active assessment",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    assessment = AssessmentDB(**existing_assessment_data.items[0])
    existing_point_data = db_point.fetch({'id_assessment': assessment.key, 'sub_bab': sub_bab})

    if existing_point_data.count == 0:
        return create_response(
            message="Empty data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    data = [Point(**x) for x in existing_point_data.items]
    dict_data = [x.dict() for x in data]
    response_data = sorted(dict_data, key=lambda x: x['point'])

    return create_response(
        message="Fetch data success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=response_data
    )


@router.get('/assessment/{key}', tags=['General'])
async def get_assessment_detail(key: str, sub_bab: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    existing_assessment = db_assessment.get(key)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    existing_point = db_point.fetch({'id_assessment': key, 'sub_bab': sub_bab})
    if existing_point.count == 0:
        return create_response(
            message="Empty data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    data = [Point(**x) for x in existing_point.items]
    dict_data = [x.dict() for x in data]
    point_list = sorted(dict_data, key=lambda x: x['point'])

    assessment = AssessmentDB(**existing_assessment).get_all_dict()

    response_data = {
        'assessment': assessment,
        'point': point_list
    }

    return create_response(
        message="Fetch data success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=response_data
    )


@router.get('/assessment/insight/{key}')
async def get_assessment_insight(key: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    existing_assessment = db_assessment.get(key)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    existing_point = db_point.fetch({'id_assessment': key})
    if existing_point.count == 0:
        return create_response(
            message="Empty data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    points = dict()
    for sub_bab in bab:
        points[sub_bab] = [point for point in existing_point.items if point['sub_bab'] == sub_bab]

    # print(json.dumps(points, indent=4))
    for key, value in points.items():
        existing_skor = len([skor['skor'] for skor in value if isinstance(skor['skor'], int)])
        if existing_skor == question_number[bab.index(key)]:
            points[key] = sum([skor['skor'] for skor in value])
        else:
            points[key] = None

    assessment = AssessmentDB(**existing_assessment).get_all_dict()

    response_data = {
        'assessment': assessment,
        'point': points
    }

    return create_response(
        message="Fetch data success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=response_data
    )


@router.get("/assessments", tags=['Deterrence - Admin'])
async def get_all_assessment(user: UserDB = Depends(get_user)) -> JSONResponse:
    # if user.role not in ['admin', 'reviewer']:
    #     return create_response(
    #         message="Forbidden access",
    #         success=False,
    #         status_code=status.HTTP_403_FORBIDDEN
    #     )

    existing_assessments_data = db_assessment.fetch({'id_institution': user.id_institution})
    if existing_assessments_data.count == 0:
        return create_response(
            message="Empty data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    raw_data = [AssessmentDB(**x) for x in existing_assessments_data.items]
    data = [assessment.get_all_dict() for assessment in raw_data]

    return create_response(
        message="Success fetch data",
        success=True,
        status_code=status.HTTP_200_OK,
        data=data
    )


@router.get("/assessments/progress", tags=['Deterrence - Admin'])
async def get_finished_assessments(user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role not in ['admin', 'staff']:
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    existing_assessment = db_assessment.fetch({'id_admin': user.key, 'selesai': False})
    if existing_assessment.count == 0:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    assessment = existing_assessment.items[0]

    existing_points = [db_point.fetch({'id_assessment': assessment['key'], 'sub_bab': sub_bab}) for sub_bab in bab]
    points_status = [point.count for point in existing_points]

    point_finished = []
    for i in range(len(bab)):
        if points_status[i] >= question_number[i]:
            point_finished.append(bab[i])

    return create_response(
        message="Success fetch data",
        success=True,
        status_code=status.HTTP_200_OK,
        data=point_finished
    )


@router.post("/selesai", tags=['Deterrence - Admin'])
async def selesai_isi(request: Request, id_assessment: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role not in ['admin', 'staff']:
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    existing_points = db_point.fetch({'id_assessment': id_assessment})
    if existing_points.count < 100:
        return create_response(
            message="Unfinished assessment",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    assessment = db_assessment.get(id_assessment)
    assessment['selesai'] = True
    key = assessment['key']
    del assessment['key']
    db_assessment.update(assessment, key=key)

    if request.client:
        create_log(
            user=user,
            event=Event.submitted_assessment,
            detail={
                'id_assessment': key,
            },
            host=request.client.host
        )

        notification_receivers = db_user.fetch({'id_institution': user.id_institution, 'role': 'reviewer'})
        if notification_receivers.count > 0:
            receivers_id = [receiver['key'] for receiver in notification_receivers.items]
            create_notification(
                receivers=receivers_id,
                event=Event.submitted_assessment,
                message="There's a new assessment to review",
                host=request.client.host
            )

    return create_response(
        message="Assessment finished",
        success=True,
        status_code=status.HTTP_200_OK,
        data=assessment
    )


@app.post("/report", tags=['Detection - Staff'])
async def get_beneish_score(data: ReportInput, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role not in ['staff', 'admin']:
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )
    report = data.dict()

    dsri = (data.account_receivables_2 / data.revenue_2) / (data.account_receivables_1 / data.revenue_1)
    gmi = (data.cogs_1 / data.revenue_1) / (data.cogs_2 / data.revenue_2)
    aqi = (1 - (data.current_assets_2 + data.ppe_2 + data.securities_2) / data.total_asset_2) / (
                1 - (data.current_assets_1 + data.ppe_1 + data.securities_1) / data.total_asset_1)
    sgi = data.revenue_2 / data.revenue_1
    depi = (data.depreciation_1 / (data.depreciation_1 + data.ppe_1)) / (data.depreciation_2 / (data.depreciation_2 + data.ppe_2))
    sgai = data.sgae_2 / data.revenue_2 / (data.sgae_1 / data.revenue_1)
    lvgi = (data.total_ltd_2 / data.total_asset_2) / (data.total_ltd_1 / data.total_asset_1)
    tata = (data.net_continuous_2 - data.cash_flow_operate_2) / data.total_asset_2

    # Calculate Beneish M-Score
    m_score = (
                -4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)

    report['beneish_m'] = m_score
    report['id_institution'] = user.id_institution
    report['dsri'] = dsri
    report['gmi'] = gmi
    report['aqi'] = aqi
    report['sgi'] = sgi
    report['depi'] = depi
    report['sgai'] = sgai
    report['lvgi'] = lvgi
    report['tata'] = tata
    report_object = Report(**report)
    db_report.insert(report_object.dict())
    return create_response(
        message="Success insert report",
        success=True,
        status_code=status.HTTP_201_CREATED,
        data=report
    )


@router.get("/assessments/list", tags=['Deterrence - Reviewer'])
async def get_evaluation(user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'reviewer':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    external = user.get_institution()['key'] == 'external'

    if external:
        existing_assessments = db_assessment.fetch({'id_reviewer_internal?ne': None, 'selesai': True})
    else:
        existing_assessments = db_assessment.fetch({'id_institution': user.id_institution, 'id_reviewer_internal': None, 'selesai': True})

    if existing_assessments.count == 0:
        return create_response(
            message='Empty data',
            success=True,
            status_code=status.HTTP_200_OK
        )

    assessments_list = [AssessmentDB(**assessment).get_all_dict() for assessment in existing_assessments.items]

    return create_response(
        message="Successfully fetch assessments",
        success=True,
        status_code=status.HTTP_200_OK,
        data=assessments_list
    )


@router.get("/assessments/finish", tags=['Deterrence - Reviewer'])
async def finish_reviewing(id_assessment: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'reviewer':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    existing_assessment = db_assessment.get(id_assessment)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    external = user.get_institution()['key'] == 'external'

    existing_points = db_point.fetch({'id_assessment': id_assessment})
    total = sum([skor['skor'] for skor in existing_points.items])

    if external:
        existing_assessment['hasil_external'] = total
    else:
        existing_assessment['hasil_internal'] = total

    current_datetime = datetime.now()
    extra_datetime = current_datetime + timedelta(hours=7)

    existing_assessment['tanggal_nilai'] = extra_datetime.strftime('%d %B %Y, %H:%M')

    key = existing_assessment['key']
    del existing_assessment['key']
    db_assessment.update(existing_assessment, key)

    return create_response(
        message="Reviewer finished",
        success=True,
        status_code=status.HTTP_200_OK,
        data=existing_assessment
    )


@router.get("/assessments/evaluation", tags=['Deterrence - Reviewer'])
async def start_evaluation(id_assessment: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'reviewer':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    existing_assessment = db_assessment.get(id_assessment)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    external = user.get_institution()['key'] == 'external'
    key = existing_assessment['key']
    del existing_assessment['key']

    if not external and existing_assessment['id_reviewer_internal']:
        return create_response(
            message="Already reviewed by another internal reviewer",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if external and not existing_assessment['id_reviewer_internal']:
        return create_response(
            message="Internal reviewer should review first",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if external and existing_assessment['id_reviewer_external']:
        return create_response(
            message="Already reviewed by another external reviewer",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if external:
        existing_assessment['id_reviewer_external'] = user.key
    else:
        existing_assessment['id_reviewer_internal'] = user.key

    db_assessment.update(existing_assessment, key)

    return create_response(
        message="Start reviewing success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=existing_assessment
    )


@router.post("/assessments/evaluation", tags=['Deterrence - Reviewer'])
async def evaluate_assessment(data: AssessmentEval, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'reviewer':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    if data.sub_bab not in bab:
        return create_response(
            message="Invalid sub bab",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    existing_assessment = db_assessment.get(data.id_assessment)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    external = user.get_institution()['key'] == 'external'

    reviewer_key = 'id_reviewer_external' if external else 'id_reviewer_internal'

    if not existing_assessment[reviewer_key]:
        return create_response(
            message="Assessment review not started yet",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if existing_assessment[reviewer_key] != user.key:
        return create_response(
            message="Assessment started by someone else",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if question_number[bab.index(data.sub_bab)] != len(data.skor):
        return create_response(
            message="Number of score didn't match",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    existing_points = db_point.fetch({'id_assessment': data.id_assessment, 'sub_bab': data.sub_bab})

    if existing_points.count < question_number[bab.index(data.sub_bab)]:
        return create_response(
            message="Please finish the assessment before evaluation",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    sorted_points = sorted(existing_points.items, key=lambda x: x['point'])
    for i in range(len(sorted_points)):
        sorted_points[i]['skor'] = float(data.skor[i]) if data.skor[i] != '-' else None

    for point in sorted_points:
        to_update = Point(**point)
        db_point.update(to_update.dict(), point['key'])

    return create_response(
        message="Success update data",
        success=True,
        status_code=status.HTTP_200_OK,
        data=sorted_points
    )


@router.patch("/password", tags=['General'])
async def change_password(data: ResetPassword, user: UserDB = Depends(get_user)) -> JSONResponse:
    if isinstance(user.password, SecretStr):
        if not authenticate_user(db_user, user.username, data.current_password):
            return create_response(
                message="Password doesn't match",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    key = user.key
    new_data = user.dict()
    new_data['password'] = encrypt_password(data.new_password)
    del new_data['key']

    db_user.update(new_data, key)
    return create_response(
        message="Successfully update password",
        success=True,
        status_code=status.HTTP_200_OK
    )


# @router.get("/email/example", tags=['Development'])
# async def send_email_example() -> JSONResponse:
#     return create_response(
#         message="Nice",
#         success=True,
#         status_code=status.HTTP_418_IM_A_TEAPOT,
#         data=data.json()
#     )


@router.get("/notifications")
async def get_notifications(user: UserDB = Depends(get_user)) -> JSONResponse:
    response_data = db_notification.fetch({'id_receiver': user.key})
    if response_data.count == 0:
        return create_response(
            message="Empty data",
            success=True,
            status_code=status.HTTP_200_OK
        )

    notification_data = response_data.items
    for notif in notification_data:
        del notif['key']

    return create_response(
        message="Fetch data success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=notification_data
    )


# @router.post('/excel')
# async def read_report_file(user: UserDB = Depends(get_user), file: UploadFile = File(None)):
#


@router.get('/today', include_in_schema=False)
async def get_date() -> JSONResponse:
    return create_response(
        message="Tanggal",
        success=True,
        status_code=status.HTTP_200_OK,
        data={'tanggal': datetime.now().strftime('%d %B %Y, %H:%M')}
    )


app.include_router(router)


