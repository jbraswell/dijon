from calendar import timegm
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from jose import jwt
from sqlalchemy.orm import Session

from dijon import crud, models, schemas
from dijon.conftest import Ctx
from dijon.settings import settings
from dijon.token_util import create_access_token, create_refresh_token


def get_token_post_data() -> schemas.Token:
    return {
        "grant_type": "password",
        "username": "username",
        "password": "securepassword"
    }


def get_token_post_data2() -> schemas.Token:
    return {
        "grant_type": "password",
        "username": "username2",
        "password": "securepassword2"
    }


@pytest.fixture
def db_user_1(db: Session) -> models.User:
    post_data = get_token_post_data()
    return crud.create_user(db, post_data["username"], "logintest@jrb.lol", post_data["password"])


@pytest.fixture
def db_user_2(db: Session) -> models.User:
    post_data = get_token_post_data2()
    return crud.create_user(db, post_data["username"], "logintest2@jrb.lol", post_data["password"])


def test_login_success(ctx: Ctx, db_user_1: models.User):
    post_data = get_token_post_data()
    response = ctx.client.post("/token", data=post_data)
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]


def test_create_access_token(ctx: Ctx, db_user_1: models.User):
    access_token = create_access_token(ctx.db, db_user_1)
    payload = jwt.decode(access_token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
    assert payload["sub"] == db_user_1.username
    assert payload["user_id"] == db_user_1.id
    assert payload["type"] == "access"
    exp_time_with_leeyway = timegm((datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRATION_SECONDS + 30)).utctimetuple())
    assert payload["exp"] < exp_time_with_leeyway


def test_create_refresh_token(ctx: Ctx, db_user_1: models.User):
    refresh_token = create_refresh_token(ctx.db, db_user_1)
    payload = jwt.decode(refresh_token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
    assert payload["sub"] == db_user_1.username
    assert payload["user_id"] == db_user_1.id
    assert payload["type"] == "refresh"
    assert payload["exp"] > timegm((datetime.utcnow() + timedelta(days=29)).utctimetuple())
    assert payload["exp"] < timegm((datetime.utcnow() + timedelta(days=31)).utctimetuple())


def test_refresh_a_token(ctx: Ctx, db_user_1: models.User):
    refresh_token = create_refresh_token(ctx.db, db_user_1)
    post_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    with patch("dijon.token_util.get_refresh_token_expiration_delta", autospec=True) as get_timedelta:
        # we have to change the time so we don't get the same token twice
        get_timedelta.return_value = datetime.utcnow() + timedelta(seconds=5)
        response = ctx.client.post("/token", data=post_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # can't reuse a refresh token
    response = ctx.client.post("/token", data=post_data)
    assert response.status_code == 401


def test_expired_tokens_deleted(ctx: Ctx, db_user_1: models.User):
    token_1 = crud.create_token(ctx.db, "dummy1", db_user_1.id, datetime.utcnow() - timedelta(days=1, seconds=30))
    token_2 = crud.create_token(ctx.db, "dummy2", db_user_1.id, datetime.utcnow() - timedelta(days=1, seconds=30))
    token_3 = crud.create_token(ctx.db, "dummy3", db_user_1.id, datetime.utcnow() - timedelta(days=1, seconds=30))
    token_4 = crud.create_token(ctx.db, "dummy4", db_user_1.id, datetime.utcnow() - timedelta(days=1, seconds=30))
    token_5 = crud.create_token(ctx.db, "dummy5", db_user_1.id, datetime.utcnow())
    token_6 = crud.create_token(ctx.db, "dummy6", db_user_1.id, datetime.utcnow() + timedelta(days=1))
    crud.delete_expired_tokens(ctx.db)
    assert not crud.token_exists(ctx.db, token_1.token)
    assert not crud.token_exists(ctx.db, token_2.token)
    assert not crud.token_exists(ctx.db, token_3.token)
    assert not crud.token_exists(ctx.db, token_4.token)
    assert crud.token_exists(ctx.db, token_5.token)
    assert crud.token_exists(ctx.db, token_6.token)


def test_login_bad_username(ctx: Ctx, db_user_1: models.User):
    post_data = get_token_post_data()
    post_data["username"] = "bad"
    response = ctx.client.post("/token", data=post_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Unauthorized"


def test_login_bad_password(ctx: Ctx, db_user_1: models.User):
    post_data = get_token_post_data()
    post_data["password"] = "bad"
    response = ctx.client.post("/token", data=post_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Unauthorized"


def test_logout_success(ctx: Ctx, db_user_1: models.User):
    access_token = create_access_token(ctx.db, db_user_1)
    refresh_token = create_refresh_token(ctx.db, db_user_1)
    post_data = {"refresh_token": refresh_token}
    headers = {"Authorization": f"bearer {access_token}"}
    response = ctx.client.post("/logout", json=post_data, headers=headers)
    assert response.status_code == 200
    assert not crud.token_exists(ctx.db, access_token)
    assert not crud.token_exists(ctx.db, refresh_token)

    # make sure trying again fails
    response = ctx.client.post("/logout", json=post_data, headers=headers)
    assert response.status_code == 401


def test_logout_fail_unauthenticated(ctx: Ctx, db_user_1: models.User):
    refresh_token = create_refresh_token(ctx.db, db_user_1)
    post_data = {"refresh_token": refresh_token}
    response = ctx.client.post("/logout", json=post_data)
    assert response.status_code == 401


def test_logout_fail_user_mismatch(ctx: Ctx, db_user_1: models.User, db_user_2: models.User):
    access_token_1 = create_access_token(ctx.db, db_user_1)
    refresh_token_2 = create_refresh_token(ctx.db, db_user_2)
    post_data = {"refresh_token": refresh_token_2}
    headers = {"Authorization": f"bearer {access_token_1}"}
    response = ctx.client.post("/logout", json=post_data, headers=headers)
    assert response.status_code == 403
