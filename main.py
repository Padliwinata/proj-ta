from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from models import RegisterForm
from db import db_user
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


@app.get('/register')
async def register(data: RegisterForm):
    db_user.put(dict(data))
    return dict(data)


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


