from dijon import crud
from dijon.conftest import Ctx


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
