from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from models.User import User


def fake_decode_token(token):
    user = {"id": 1, "token": "1233456", "disabled": False}
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Auth:
    def __init__(self):
        self._current_user = {"id": 1, "token": "1233456", "disabled": False}

    def login(self, token: str = Depends(oauth2_scheme)):
        self._current_user = fake_decode_token(token)
        if not self._current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return self._current_user

    def get_current_active_user(self):
        if self._current_user["disabled"]:
            raise HTTPException(status_code=400, detail="Inactive user")
        return self._current_user
