import json
from enum import Enum
import typing
from datetime import datetime

from pydantic import BaseModel, SecretStr, EmailStr, AnyUrl

from db import db_institution, db_user


class UserRole(str, Enum):
    admin = "admin"
    super_admin = "super admin"
    staff = "staff"
    reviewer = "reviewer"


class RegisterForm(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr
    full_name: str
    role: UserRole
    phone: str
    institution_name: str
    institution_address: str
    institution_phone: str
    institution_email: EmailStr


class Institution(BaseModel):
    name: str
    address: str
    phone: str
    email: EmailStr


class InstitutionDB(Institution):
    key: str


class Response(BaseModel):
    success: bool
    code: int
    message: str
    data: typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any], None]


class ResponseDev(Response):
    access_token: typing.Optional[str]


class User(BaseModel):
    username: str
    full_name: str
    password: typing.Union[SecretStr, bytes, None]
    email: str
    role: UserRole = UserRole.admin
    id_institution: str
    is_active: bool

    def get_institution(self) -> typing.Dict[str, typing.Any]:
        institution = db_institution.get(self.id_institution)
        data = InstitutionDB(**institution)
        return data.dict()


class UserDB(User):
    key: str


class AddUser(BaseModel):
    username: str
    email: EmailStr
    password: typing.Optional[SecretStr]
    role: UserRole = UserRole.admin


class Refresh(BaseModel):
    refresh_token: str


class Payload(BaseModel):
    sub: str
    role: str
    iat: int


class Log(BaseModel):
    name: str
    email: str
    role: UserRole
    tanggal: str
    id_institution: str


class Proof(BaseModel):
    id_user: str
    url: str
    file_name: str


class ProofMeta(BaseModel):
    bab: str
    sub_bab: str
    point: int
    answer: int


class Point(BaseModel):
    id_assessment: str
    bab: str
    sub_bab: str
    point: int
    answer: int
    skor: int
    proof: Proof


class PointDB(Point):
    key: str


class SubPoint(BaseModel):
    point: int
    proof: Proof


class FileMeta(BaseModel):
    bab: str
    sub_bab: str
    point: int


class Assessment(BaseModel):
    id_institution: str
    id_admin: str
    id_reviewer: typing.Optional[str]
    tanggal: str
    hasil: int
    selesai: bool

    def get_admin(self) -> str:
        data = db_user.get(self.id_admin)
        name: str = data['full_name']
        return name

    def get_reviewer(self) -> str:
        if self.id_reviewer == '':
            return ''
        reviewer = db_user.get(self.id_reviewer)
        name: str = reviewer['full_name']
        return name

    def get_all_dict(self) -> typing.Dict[str, typing.Any]:
        data = super().dict()
        data['nama_admin'] = self.get_admin()
        data['nama_reviewer'] = self.get_reviewer()
        return data


class AssessmentDB(Assessment):
    key: str


class AssessmentEval(BaseModel):
    id_assessment: str
    sub_bab: str
    skor: typing.List[int]


class Report(BaseModel):
    revenue: float
    cogs: float
    sgae: float
    depreciation: float
    net_continuous: float
    account_receivables: float
    current_assets: float
    ppe: float
    securities: float
    total_asset: float
    current_liabilities: float
    total_ltd: float
    cash_flow_operate: float
    dsri: float
    gmi: float
    aqi: float
    sgi: float
    depi: float
    sgai: float
    lvgi: float
    tata: float
    beneish_m: float


