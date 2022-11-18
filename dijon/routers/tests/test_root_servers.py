import pytest
from sqlalchemy.orm import Session

from dijon import crud, schemas
from dijon.conftest import Ctx


@pytest.fixture
def headers(db: Session, admin_access_token: str) -> dict[str, str]:
    headers = {"Authorization": f"bearer {admin_access_token}"}
    return headers


def test_list_root_servers(ctx: Ctx, headers: dict[str, str]):
    response = ctx.client.get("/rootservers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data == []

    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    rs_2 = crud.create_root_server(ctx.db, "root 2", "https://2/main_server/", True)

    response = ctx.client.get("/rootservers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == rs_1.id
    assert data[0]["name"] == rs_1.name
    assert data[0]["url"] == rs_1.url
    assert data[1]["id"] == rs_2.id
    assert data[1]["name"] == rs_2.name
    assert data[1]["url"] == rs_2.url


def test_get_root_server(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)

    response = ctx.client.get(f"/rootservers/{rs_1.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rs_1.id
    assert data["name"] == rs_1.name
    assert data["url"] == rs_1.url

    response = ctx.client.get(f"/rootservers/{rs_1.id + 1}", headers=headers)
    assert response.status_code == 404


def test_create_root_server_enabled(ctx: Ctx, headers: dict[str, str]):
    response = ctx.client.post(
        "/rootservers",
        json=schemas.RootServerCreate(
            name="SEZF",
            url="https://reallygoodurl/main_server",
            is_enabled=True
        ).dict(),
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["name"] == "SEZF"
    assert data["url"] == "https://reallygoodurl/main_server/"
    assert data["is_enabled"] is True


def test_create_root_server_disabled(ctx: Ctx, headers: dict[str, str]):
    response = ctx.client.post(
        "/rootservers",
        json=schemas.RootServerCreate(
            name="SEZF",
            url="https://reallygoodurl/main_server",
            is_enabled=False
        ).dict(),
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["name"] == "SEZF"
    assert data["url"] == "https://reallygoodurl/main_server/"
    assert data["is_enabled"] is False


def test_delete_root_server(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)

    response = ctx.client.delete(f"/rootservers/{rs_1.id}", headers=headers)
    assert response.status_code == 204
    response = ctx.client.delete(f"/rootservers/{rs_1.id}", headers=headers)
    assert response.status_code == 404


def test_update_root_server_name(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    payload = schemas.RootServerUpdate(name="blah")
    response = ctx.client.patch(
        f"/rootservers/{rs_1.id}",
        json=payload.dict(),
        headers=headers
    )
    assert response.status_code == 204
    root_server = crud.get_root_server(ctx.db, rs_1.id)
    assert root_server.name == payload.name


def test_update_root_server_url(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    payload = schemas.RootServerUpdate(url="https://2/main_server/")
    response = ctx.client.patch(
        f"/rootservers/{rs_1.id}",
        json=payload.dict(),
        headers=headers
    )
    assert response.status_code == 204
    root_server = crud.get_root_server(ctx.db, rs_1.id)
    assert root_server.url == payload.url
    assert root_server.is_enabled is True


def test_update_root_server_is_enabled(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    payload = schemas.RootServerUpdate(is_enabled=False)
    response = ctx.client.patch(
        f"/rootservers/{rs_1.id}",
        json=payload.dict(),
        headers=headers
    )
    assert response.status_code == 204
    root_server = crud.get_root_server(ctx.db, rs_1.id)
    assert root_server.is_enabled is False


def test_update_root_server_no_fields(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    payload = schemas.RootServerUpdate()
    response = ctx.client.patch(
        f"/rootservers/{rs_1.id}",
        json=payload.dict(),
        headers=headers
    )
    assert response.status_code == 204
    root_server = crud.get_root_server(ctx.db, rs_1.id)
    assert root_server.name == rs_1.name
    assert root_server.url == rs_1.url


def test_update_root_server_not_found(ctx: Ctx, headers: dict[str, str]):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    payload = schemas.RootServerUpdate(url="https://2/main_server/")
    response = ctx.client.patch(
        "/rootservers/2",
        json=payload.dict(),
        headers=headers
    )
    assert response.status_code == 404
    root_server = crud.get_root_server(ctx.db, rs_1.id)
    assert root_server.url == rs_1.url
