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


class Event(str, Enum):
    logged_in = "Logged In"
    logged_out = "Logged Out"

    activated_admin = "Activated Admin"
    deactivated_admin = "Deactivated Admin"

    activated_staff = "Activated Staff"
    deactivated_staff = "Deactivated Staff"
    started_assessment = "Started Assessment"
    viewed_assessments = "Viewed Assessments"
    deleted_assessments = "Deleted Assessments"
    submit_point = "Submit Point"
    edited_point = "Edited Point"
    uploaded_file = "Uploaded File"
    deleted_file = "Deleted File"
    submitted_assessment = "Submitted Assessment"

    started_review = "Started Review"
    finished_review = "Finished Review"



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


class CustomResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any], None]


class CustomResponseDev(CustomResponse):
    access_token: typing.Optional[str]


class User(BaseModel):
    username: str
    full_name: str
    password: typing.Union[SecretStr, bytes, None]
    email: str
    role: UserRole = UserRole.admin
    id_institution: str
    is_active: bool
    phone: str

    def get_institution(self) -> typing.Dict[str, typing.Any]:
        institution = db_institution.get(self.id_institution)
        data = InstitutionDB(**institution)
        return data.dict()


class UserDB(User):
    key: str


class AddUser(BaseModel):
    full_name: str
    role: UserRole
    phone: str
    email: str
    username: str
    password: str


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
    event: typing.Optional[Event]
    detail: typing.Optional[typing.Dict[str, typing.Any]]
    id_institution: str


class Notification(BaseModel):
    id_receiver: str
    event: Event
    message: str
    date: str


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
    skor: typing.Optional[int]
    proof: typing.Optional[Proof]


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
    id_reviewer_internal: typing.Optional[str]
    id_reviewer_external: typing.Optional[str]
    tanggal: str
    hasil_internal: typing.Optional[int]
    hasil_external: typing.Optional[int]
    selesai: bool

    def get_admin(self) -> str:
        data = db_user.get(self.id_admin)
        name: str = data['full_name']
        return name

    def get_reviewer_internal(self) -> str:
        if not self.id_reviewer_internal:
            return ''
        data = db_user.get(self.id_reviewer_internal)
        name: str = data['full_name']
        return name

    def get_reviewer_external(self) -> str:
        if not self.id_reviewer_external:
            return ''
        data = db_user.get(self.id_reviewer_external)
        name: str = data['full_name']
        return name

    def get_all_dict(self) -> typing.Dict[str, typing.Any]:
        data = super().dict()
        data['admin'] = self.get_admin()
        data['reviewer_internal'] = self.get_reviewer_internal()
        data['reviewer_external'] = self.get_reviewer_external()
        return data


class AssessmentDB(Assessment):
    key: str


class AssessmentEval(BaseModel):
    id_assessment: str
    sub_bab: str
    skor: typing.List[str]


class ReportInput(BaseModel):
    revenue_1: float
    cogs_1: float
    sgae_1: float
    depreciation_1: float
    net_continuous_1: float
    account_receivables_1: float
    current_assets_1: float
    ppe_1: float
    securities_1: float
    total_asset_1: float
    current_liabilities_1: float
    total_ltd_1: float
    cash_flow_operate_1: float
    revenue_2: float
    cogs_2: float
    sgae_2: float
    depreciation_2: float
    net_continuous_2: float
    account_receivables_2: float
    current_assets_2: float
    ppe_2: float
    securities_2: float
    total_asset_2: float
    current_liabilities_2: float
    total_ltd_2: float
    cash_flow_operate_2: float
    tahun_1: float
    tahun_2: float
    id_institution: str
    beneish_m: float


class Report(ReportInput):
    id_institution: str
    beneish_m: float


class ResetPassword(BaseModel):
    current_password: str
    new_password: str

