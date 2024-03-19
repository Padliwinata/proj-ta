from enum import Enum
import typing

from pydantic import BaseModel, SecretStr, EmailStr

from db import db_institution


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
    key: str
    name: str
    address: str
    phone: str
    email: EmailStr


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
        data = Institution(**institution)
        return data.dict()


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




