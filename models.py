from pydantic import BaseModel, SecretStr


class RegisterForm(BaseModel):
    username: str
    email: str
    password: SecretStr

