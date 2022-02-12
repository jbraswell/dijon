from datetime import datetime, timedelta

from dijon import crud
from dijon.conftest import Ctx


def test_list_snapshots(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 2", "https://2/main_server/")
    crud.create_snapshot(ctx.db, rs_1)
    snap_2_rs_1 = crud.create_snapshot(ctx.db, rs_1)
    crud.create_snapshot(ctx.db, rs_2)
    snap_2_rs_2 = crud.create_snapshot(ctx.db, rs_2)
    snap_2_rs_1.created_at = datetime.utcnow() + timedelta(weeks=1)
    snap_2_rs_2.created_at = datetime.utcnow() + timedelta(weeks=1)
    ctx.db.add_all([snap_2_rs_1, snap_2_rs_2])
    ctx.db.flush()

    response = ctx.client.get("/snapshots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


def test_list_server_snapshots(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 2", "https://2/main_server/")

    crud.create_snapshot(ctx.db, rs_1)
    crud.create_snapshot(ctx.db, rs_1)
    snap_3_rs_1 = crud.create_snapshot(ctx.db, rs_1)
    snap_3_rs_1.created_at = datetime.utcnow() + timedelta(weeks=1)
    ctx.db.add(snap_3_rs_1)
    ctx.db.flush()
    crud.create_snapshot(ctx.db, rs_2)

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_server_snapshot(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    crud.create_snapshot(ctx.db, rs_1)
    snap_2 = crud.create_snapshot(ctx.db, rs_1)
    snap_2.created_at = datetime.utcnow() + timedelta(weeks=1)
    ctx.db.add(snap_2)
    ctx.db.flush()

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots/{snap_2.created_at.date()}")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == str(snap_2.created_at.date())
