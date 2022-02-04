import pytest
from sqlalchemy.orm import Session

from dijon import crud, models, schemas
from dijon.conftest import Ctx
from dijon.routers.login import create_access_token


@pytest.fixture
def user(db: Session) -> models.User:
    return crud.create_user(db, "username", "nobody@jrb.lol", "password")


@pytest.fixture
def headers(db: Session, user: models.User) -> dict[str, str]:
    # TODO creating access tokens is slow, so precreate an admin user
    # TODO and token for the duration of all tests
    access_token = create_access_token(db, user)
    headers = {"Authorization": f"bearer {access_token}"}
    return headers


def get_user_create_schema() -> schemas.UserCreate:
    return schemas.UserCreate(
        username="user1",
        email="email@example.com",
        password="password",
        is_active=True,
        is_admin=True
    )


def test_create_user_username(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.username = "user1"
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_create.username


def test_create_user_email(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.email = "email@example.com"
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_create.email


def test_create_user_is_active(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.is_active = True
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is True


def test_create_user_is_not_active(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.is_active = False
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is False


def test_create_user_is_admin(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.is_admin = True
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["is_admin"] is True


def test_create_user_is_not_admin(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.is_admin = False
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["is_admin"] is False


def test_create_user_password(ctx: Ctx, headers: dict[str, str]):
    user_create = get_user_create_schema()
    user_create.password = "blah"
    response = ctx.client.post("/users", json=user_create.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
