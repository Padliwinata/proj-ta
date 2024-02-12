from typing import Annotated, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm

from models import RegisterForm
from dependencies import *

app = FastAPI()


@app.get('/put')
async def index():
    db_user.put({'username': 'example'})
    return {"username": "example"}


@app.get('/get')
async def get_data():
    res = db_user.fetch()
    return {"data": res.items}


@app.post('/register')
async def register(data: RegisterForm):
    data.password = f.encrypt(data.password.get_secret_value().encode('utf-8')).decode('utf-8')
    db_user.put(dict(data))
    response = {'username': data.username}
    return response


@app.post("/auth")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = {'sub': form_data.username}
    access_token = create_token(data)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/auth")
async def check(x_token: Optional[str] = Header(None)):
    if x_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credential not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(x_token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


