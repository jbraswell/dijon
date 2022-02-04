from typing import Optional

from dynaconf import settings
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:  # noqa: E722
        db.rollback()
        raise
    finally:
        db.close()


class Context:
    def __init__(
        self,
        token: str = Security(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        db: Session = Depends(get_db)
    ):
        self.db = db
        self._token: str = None
        self._user: models.User = None
        if token is not None and self._is_token_valid(token):
            self._token = token

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_authenticated(self) -> bool:
        return self.token is not None

    @property
    def is_admin(self) -> bool:
        return self.user is not None and self.user.is_admin

    @property
    def user(self) -> Optional[models.User]:
        if self._user is None:
            if self._token is not None:
                token = crud.get_token(self.db, self._token)
                if token is not None:
                    self._user = token.user
        return self._user

    def _is_token_valid(self, token):
        try:
            payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        except JWTError:
            return False

        token_type = payload.get("type")
        if token_type is None or token_type != "access":
            return False

        if payload.get("sub") is None:
            return False

        user_id = payload.get("user_id")
        if user_id is None:
            return False

        if not crud.token_exists(self.db, token):
            return False

        db_user = crud.get_user_by_id(self.db, user_id)
        if not db_user.is_active:
            return False

        return True
