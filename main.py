import io
import json
from typing import Annotated, Union, List
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, status, File, UploadFile, Request, APIRouter
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import SecretStr, AnyUrl

from dependencies import (
    authenticate_user,
    create_refresh_token,
    create_access_token,
    TokenResponse,
    get_payload_from_token,
    create_response
)

from db import (
    db_user,
    db_institution,
    db_log,
    db_point,
    db_proof,
    drive,
    db_assessment,
    db_report
)
from exceptions import DependencyException
from models import (
    RegisterForm,
    Response,
    User,
    Refresh,
    ResponseDev,
    AddUser,
    Institution,
    Log,
    ProofMeta,
    Point,
    Proof,
    UserDB,
    AssessmentDB,
    Assessment,
    AssessmentEval,
    PointDB,
    Report,
    ReportInput
)
from mailer import send_confirmation
from settings import SECRET_KEY, ALGORITHM, DEVELOPMENT
from seeder import seed, delete_db, seed_assessment

app = FastAPI()
router = APIRouter(prefix='/api')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth', auto_error=False)
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


@router.post('/register', tags=['General', 'Auth'])
async def register(data: RegisterForm) -> JSONResponse:
    existing_data = db_user.fetch([{'username': data.username}, {'email': data.email}])
    if existing_data.count > 0:
        return create_response(
            message="Username or email already "
        )

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
    res = db_user.put(json.loads(new_user.json()))

    userid: str = res['key']
    send_confirmation(userid, new_user.email, new_user.full_name)

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


@router.post("/auth", tags=['General', 'Auth'])
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

    log_data = Log(name=form_data.username, email=user.email, role=user.role, tanggal=datetime.now().strftime('%d %B %Y, %H:%M'), id_institution=user.id_institution)
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


@router.get("/auth", tags=['General'])
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


@router.put("/auth", tags=['General'])
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


@router.post("/account", tags=['Admin'])
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


@router.post('/document_1', include_in_schema=False)
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


@router.delete("/test", include_in_schema=False)
async def delete_test_data() -> Response:
    data = db_user.fetch(test_data)
    db_user.delete(data.items[0]['key'])

    return Response(
        success=True,
        code=status.HTTP_200_OK,
        message="Successfully deleted",
        data=None
    )


@router.get("/admin", tags=['Super Admin'])
async def get_admin_list(user: User = Depends(get_user)) -> JSONResponse:
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


@router.get("/staff")
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
            'status': parsed_user['is_active']
        })

    return create_response(
        "Success fetch data",
        True,
        status.HTTP_200_OK,
        data=final_data
    )
    # for data in fetch_response.items:


@router.get("/log", tags=['Admin'])
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


@router.post("/point")
async def upload_proof_point(request: Request,
                             metadata: ProofMeta = Depends(),
                             user: UserDB = Depends(get_user),
                             file: UploadFile = File(None)) -> JSONResponse:

    if user.role != 'admin':
        return create_response(
            message="Forbidden Access",
            status_code=status.HTTP_403_FORBIDDEN,
            success=False
        )

    content = None
    if file:
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
        skor=0
    )

    db_point.put(json.loads(new_point.json()))

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

    assessment = existing_assessment_data.items[0]

    existing_points = [db_point.fetch({'id_assessment': assessment['key'], 'sub_bab': sub_bab}) for sub_bab in bab]
    points_status = [point.count for point in existing_points]

    point_finished = []
    for i in range(len(bab)):
        if points_status[i] >= question_number[i]:
            point_finished.append(bab[i])

    if len(point_finished) == 10:
        assessment['selesai'] = True
        db_assessment.update(assessment, key=assessment['key'])

    return create_response(
        message=filename,
        status_code=status.HTTP_200_OK,
        success=True,
        data=data
    )


@router.post("/proofs", include_in_schema=False)
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


@router.get("/seed", tags=['Testing'])
async def seed_database() -> JSONResponse:
    seed()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@router.get("/seed/assessment")
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


@router.get("/delete", tags=['Testing'])
async def delete_database() -> JSONResponse:
    delete_db()
    return create_response(
        message="Success",
        status_code=status.HTTP_200_OK,
        success=True
    )


@router.get("/file/{filename}", tags=["General"])
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
async def get_actual_file(filename: str) -> StreamingResponse:
    response = drive.get(filename)
    content = response.read()

    file_like = io.BytesIO(content)

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}.pdf"'
    }
    return StreamingResponse(file_like, headers=headers)


@router.get("/verify/{userid}", tags=['Auth'])
async def verify_user(userid: str) -> JSONResponse:
    resp = db_user.get(userid)
    if not resp:
        return create_response(
            message="User not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    user = UserDB(**resp)
    user.is_active = True

    db_user.update(
        {'is_active': True},
        user.key
    )

    # user_data = json.loads(user.json())

    return create_response(
        message="User activated",
        success=True,
        status_code=status.HTTP_200_OK,
    )


@router.post("/assessment")
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
        'id_reviewer': '',
        'tanggal': datetime.now().strftime('%d %B %Y, %H:%M'),
        'hasil': 0,
        'selesai': False
    }

    db_assessment.put(new_assessment)

    return create_response(
        message="Start assessment success",
        success=True,
        status_code=status.HTTP_201_CREATED,
        data=new_assessment
    )


@router.get("/assessment")
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
    response_data = [x.dict() for x in data]

    return create_response(
        message="Fetch data success",
        success=True,
        status_code=status.HTTP_200_OK,
        data=response_data
    )


@router.get("/assessments")
async def get_all_assessment(user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role not in ['admin', 'reviewer']:
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

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


@router.get("/assessments/progress")
async def get_finished_assessments(user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
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


@router.post("/assessments/evaluation", tags=['Reviewer'])
async def evaluate_assessment(data: AssessmentEval, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'reviewer':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )

    existing_assessment = db_assessment.get(data.id_assessment)
    if not existing_assessment:
        return create_response(
            message="Assessment not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND
        )

    if existing_assessment['id_reviewer'] != '':
        return create_response(
            message="Already reviewed by another reviewer",
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
        sorted_points[i]['skor'] = data.skor[i]

    for point in sorted_points:
        to_update = Point(**point)
        db_point.update(to_update.dict(), point['key'])

    # existing_assessment['hasil'] = sum([point['skor'] for point in sorted_points]) + existing_assessment['hasil']
    # key = existing_assessment['key']
    # del existing_assessment['key']
    # db_assessment.update(existing_assessment, key=key)

    return create_response(
        message="Success update data",
        success=True,
        status_code=status.HTTP_200_OK,
        data=sorted_points
    )


@router.post("/selesai")
async def selesai_isi(id_assessment: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'admin':
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

    return create_response(
        message="Assessment finished",
        success=True,
        status_code=status.HTTP_200_OK,
        data=assessment
    )


@app.post("/report")
async def get_beneish_score(data: Report, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'staff':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )
    report = data.dict()
    report['beneish_m'] = -2
    report['id_institution'] = user.id_institution
    report_object = Report(**report)
    db_report.insert(report_object.dict())
    return create_response(
        message="Success insert report",
        success=True,
        status_code=status.HTTP_201_CREATED,
        data=report_object.dict()
    )


@app.post("/deactivate")
async def deactivate_institution(id_institution: str, user: UserDB = Depends(get_user)) -> JSONResponse:
    if user.role != 'super admin':
        return create_response(
            message="Forbidden access",
            success=False,
            status_code=status.HTTP_403_FORBIDDEN
        )


app.include_router(router)




