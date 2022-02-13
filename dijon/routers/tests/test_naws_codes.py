import pytest
from sqlalchemy.orm import Session

from dijon import crud, schemas
from dijon.conftest import Ctx


@pytest.fixture
def headers(db: Session, admin_access_token: str) -> dict[str, str]:
    headers = {"Authorization": f"bearer {admin_access_token}"}
    return headers


# meeting codes
#
#
def test_create_meeting_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    post = schemas.NawsCodeCreate(bmlt_id=1, code='test')
    # unauthenticated access denied
    response = ctx.client.post(f"/rootservers/{rs.id}/meetings/nawscodes", json=post.dict())
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.post(f"/rootservers/{rs.id}/meetings/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == post.bmlt_id
    assert data["code"] == post.code
    # duplicate
    response = ctx.client.post(f"/rootservers/{rs.id}/meetings/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 409


def test_delete_meeting_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_meeting_naws_code(ctx.db, rs.id, 1, 'test')
    # unauthenticated access denied
    response = ctx.client.delete(f"/rootservers/{rs.id}/meetings/nawscodes/1")
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.delete(f"/rootservers/{rs.id}/meetings/nawscodes/1", headers=headers)
    assert response.status_code == 204
    # duplicate
    response = ctx.client.delete(f"/rootservers/{rs.id}/meetings/nawscodes/1", headers=headers)
    assert response.status_code == 404


def test_list_meeting_nawscodes(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_meeting_naws_code(ctx.db, rs_1.id, 1, "A")
    crud.create_meeting_naws_code(ctx.db, rs_2.id, 2, "B")
    response = ctx.client.get("/meetings/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_list_server_meeting_nawscodes(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_meeting_naws_code(ctx.db, rs.id, 1, "A")
    crud.create_meeting_naws_code(ctx.db, rs.id, 2, "B")
    response = ctx.client.get(f"/rootservers/{rs.id}/meetings/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_get_meeting_nawscode(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    code = crud.create_meeting_naws_code(ctx.db, rs.id, 1, "A")
    response = ctx.client.get(f"/rootservers/{rs.id}/meetings/nawscodes/1")
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == 1
    assert data["code"] == code.code


# format codes
#
#
def test_create_format_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    post = schemas.NawsCodeCreate(bmlt_id=1, code='test')
    # unauthenticated access denied
    response = ctx.client.post(f"/rootservers/{rs.id}/formats/nawscodes", json=post.dict())
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.post(f"/rootservers/{rs.id}/formats/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == post.bmlt_id
    assert data["code"] == post.code
    # duplicate
    response = ctx.client.post(f"/rootservers/{rs.id}/formats/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 409


def test_delete_format_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_format_naws_code(ctx.db, rs.id, 1, 'test')
    # unauthenticated access denied
    response = ctx.client.delete(f"/rootservers/{rs.id}/formats/nawscodes/1")
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.delete(f"/rootservers/{rs.id}/formats/nawscodes/1", headers=headers)
    assert response.status_code == 204
    # duplicate
    response = ctx.client.delete(f"/rootservers/{rs.id}/formats/nawscodes/1", headers=headers)
    assert response.status_code == 404


def test_list_formats_nawscodes(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_format_naws_code(ctx.db, rs_1.id, 1, "A")
    crud.create_format_naws_code(ctx.db, rs_2.id, 2, "B")
    response = ctx.client.get("/formats/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_list_server_format_nawscodes(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_format_naws_code(ctx.db, rs.id, 1, "A")
    crud.create_format_naws_code(ctx.db, rs.id, 2, "B")
    response = ctx.client.get(f"/rootservers/{rs.id}/formats/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_get_format_nawscode(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    code = crud.create_format_naws_code(ctx.db, rs.id, 1, "A")
    response = ctx.client.get(f"/rootservers/{rs.id}/formats/nawscodes/1")
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == 1
    assert data["code"] == code.code


# service body codes
#
#
def test_create_service_body_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    post = schemas.NawsCodeCreate(bmlt_id=1, code='test')
    # unauthenticated access denied
    response = ctx.client.post(f"/rootservers/{rs.id}/servicebodies/nawscodes", json=post.dict())
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.post(f"/rootservers/{rs.id}/servicebodies/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == post.bmlt_id
    assert data["code"] == post.code
    # duplicate
    response = ctx.client.post(f"/rootservers/{rs.id}/servicebodies/nawscodes", json=post.dict(), headers=headers)
    assert response.status_code == 409


def test_delete_service_body_naws_code(ctx: Ctx, headers: dict[str, str]):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_service_body_naws_code(ctx.db, rs.id, 1, 'test')
    # unauthenticated access denied
    response = ctx.client.delete(f"/rootservers/{rs.id}/servicebodies/nawscodes/1")
    assert response.status_code == 401
    # authenticated, good
    response = ctx.client.delete(f"/rootservers/{rs.id}/servicebodies/nawscodes/1", headers=headers)
    assert response.status_code == 204
    # duplicate
    response = ctx.client.delete(f"/rootservers/{rs.id}/servicebodies/nawscodes/1", headers=headers)
    assert response.status_code == 404


def test_list_service_body_nawscodes(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_service_body_naws_code(ctx.db, rs_1.id, 1, "A")
    crud.create_service_body_naws_code(ctx.db, rs_2.id, 2, "B")
    response = ctx.client.get("/servicebodies/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_list_server_service_body_nawscodes(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_service_body_naws_code(ctx.db, rs.id, 1, "A")
    crud.create_service_body_naws_code(ctx.db, rs.id, 2, "B")
    response = ctx.client.get(f"/rootservers/{rs.id}/servicebodies/nawscodes")
    data = response.json()
    assert len(data) == 2
    for naws_code in data:
        assert "root_server_id" in naws_code
        assert "bmlt_id" in naws_code
        assert "code" in naws_code


def test_get_service_body_nawscode(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    code = crud.create_service_body_naws_code(ctx.db, rs.id, 1, "A")
    response = ctx.client.get(f"/rootservers/{rs.id}/servicebodies/nawscodes/1")
    data = response.json()
    assert data["root_server_id"] == rs.id
    assert data["bmlt_id"] == 1
    assert data["code"] == code.code
