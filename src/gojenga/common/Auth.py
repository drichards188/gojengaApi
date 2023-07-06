from datetime import datetime, timedelta
from typing import Optional

import pytz
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel

from storage.Dynamo import Dynamo, logger


class MyAuth:
    def __init__(self):
        self.user = None


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS = 7

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    expires: Optional[datetime]


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(table_name, username: str):
    query: dict = {'name': username}
    try:
        user = Dynamo.get_item(table_name, query)
        # user["disabled"] = False
        return user
    except Exception as e:
        logger.error(e)


def authenticate_user(table_name, username: str, password: str):
    user = get_user(table_name, username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(pytz.utc) + expires_delta
    else:
        expire = datetime.now(pytz.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def renew_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()

    expire = datetime.now(pytz.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


async def get_current_user(token: str = Depends(oauth2_scheme)):
    table_name = "usersTest"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        expires = payload.get("exp")
        if username is None:
            print('username is None')
            raise credentials_exception
        token_data = TokenData(username=username, expires=expires)
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="token has been expired")
    except JWTError:
        print('JWTError')
        raise credentials_exception
    user = get_user(table_name=table_name, username=token_data.username)
    if user is None:
        print('user is None')
        raise credentials_exception
    if datetime.now(pytz.utc) > token_data.expires:
        raise HTTPException(status_code=403, detail="token has been expired")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    # if current_user["disabled"]:
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
