from pydantic import BaseModel, EmailStr, SecretStr


class RegisterForm(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr

