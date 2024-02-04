from fastapi import FastAPI
from deta import Deta

app = FastAPI()
deta = Deta("c0YK3LGkSzAM_WPS5wNp7NafechQa2id7Q7Sd9Z8UaxmZ")
db_user = deta.Base("user")


@app.get('/put')
async def index():
    db_user.put({'username': 'example'})
    return {"username": "example"}

@app.get('/get')
async def get_data():
    res = db_user.fetch()
    return {"data": res.items}
