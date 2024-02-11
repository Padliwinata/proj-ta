from fastapi import FastAPI

from models import RegisterForm
from db import db_user

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


