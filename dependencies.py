from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    
