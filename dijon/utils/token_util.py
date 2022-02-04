from datetime import datetime, timedelta

from jose import jwt
from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.settings import settings


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
