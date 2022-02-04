from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from dynaconf import settings
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from jose import JWTError, jwt
from pydantic import BaseModel, root_validator
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from dijon import crud, models, password_util, schemas
from dijon.dependencies import Context, get_db


router = APIRouter()


class GrantType(str, Enum):
    password = "password"
    refresh_token = "refresh_token"


class OAuth2RequestForm:
    class Validator(BaseModel):
        grant_type: GrantType
        username: Optional[str]
        password: Optional[str]
        refresh_token: Optional[str]

        @root_validator
        def has_required_fields(cls, v):
            has_username = "username" in v and bool(v["username"])
            has_password = "password" in v and bool(v["password"])
            has_refresh_token = "refresh_token" in v and bool(v["refresh_token"])
            grant_type = v["grant_type"]

            if grant_type == GrantType.password:
                if not has_username or not has_password:
                    raise ValueError("username and password are required for password grant_type")
                if has_refresh_token:
                    raise ValueError("refresh_token cannot be provided for password grant_type")
            elif grant_type == GrantType.refresh_token:
                if not has_refresh_token:
                    raise ValueError("refresh_token is required for refresh_token grant type")
                if has_username or has_password:
                    raise ValueError("username and password cannot be provided for refresh_token grant type")

            return v

    def __init__(
        self,
        grant_type: str = Form(..., regex="password|refresh_token"),
        username: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        refresh_token: Optional[str] = Form(None),
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.Validator(grant_type=grant_type, username=username, password=password, refresh_token=refresh_token)
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token


def get_access_token_expiration_delta():
    return datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRATION_SECONDS)


def get_refresh_token_expiration_delta():
    return datetime.utcnow() + timedelta(days=30)


def create_access_token(db: Session, db_user: models.User):
    return _create_token(db, db_user, "access")


def create_refresh_token(db: Session, db_user: models.User):
    return _create_token(db, db_user, "refresh")


def _create_token(db: Session, db_user: models.User, token_type: str):
    expires_at = get_refresh_token_expiration_delta() if token_type == "refresh" else get_access_token_expiration_delta()
    data = {
        "sub": db_user.username,
        "user_id": db_user.id,
        "exp": expires_at,
        "type": "refresh" if token_type == "refresh" else "access"
    }
    token = jwt.encode(data, settings.TOKEN_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
    crud.create_token(db, token, db_user.id, expires_at)
    return token


@router.post("/token", response_model=schemas.Token)
def create_auth_token(form_data: OAuth2RequestForm = Depends(), db: Session = Depends(get_db)):
    if form_data.grant_type == GrantType.password:
        db_user = crud.get_user_by_username(db, form_data.username)
        if not db_user:
            password_util.hash("dummy")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        if not password_util.verify(form_data.password, db_user.hashed_password):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    else:
        if not crud.token_exists(db, form_data.refresh_token):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(form_data.refresh_token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        token_type = payload.get("type")
        if token_type is None or token_type != "refresh":
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        if payload.get("sub") is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        db_user = crud.get_user_by_id(db, user_id)
        if db_user is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        if not db_user.is_active:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        crud.delete_token(db, form_data.refresh_token)

    # If we get too big and this gets too slow, we'll have some watchdog process
    # that deletes them on some cadence
    crud.delete_expired_tokens(db)

    return {
        "access_token": create_access_token(db, db_user),
        "refresh_token": create_refresh_token(db, db_user),
        "token_type": "bearer"
    }


@router.post("/logout", status_code=HTTP_200_OK, response_class=Response)
def logout(logout: schemas.Logout, ctx: Context = Depends()):
    if not ctx.is_authenticated or not ctx.token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    try:
        payload = jwt.decode(logout.refresh_token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    if payload.get("user_id") != ctx.user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    crud.delete_token(ctx.db, ctx.token)
    crud.delete_token(ctx.db, logout.refresh_token)
