from datetime import timedelta

from dijon import crud
from dijon.conftest import Ctx


def test_list_snapshot_service_bodies(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    rs_2 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    snap_1_rs_1 = crud.create_snapshot(ctx.db, rs_1)
    snap_1_rs_2 = crud.create_snapshot(ctx.db, rs_2)
    snap_2_rs_1 = crud.create_snapshot(ctx.db, rs_1)
    snap_2_rs_2 = crud.create_snapshot(ctx.db, rs_2)
    snap_2_rs_1.created_at = snap_2_rs_1.created_at + timedelta(weeks=1)
    snap_2_rs_2.created_at = snap_2_rs_2.created_at + timedelta(weeks=1)
    ctx.db.add_all([snap_2_rs_1, snap_2_rs_2])
    ctx.db.flush()
    ctx.db.refresh(snap_2_rs_1)
    ctx.db.refresh(snap_2_rs_2)
    crud.create_service_body(ctx.db, snap_1_rs_1.id, 1, 'test', 'test')
    crud.create_service_body(ctx.db, snap_1_rs_1.id, 2, 'test', 'test')
    crud.create_service_body(ctx.db, snap_2_rs_1.id, 3, 'test', 'test')
    crud.create_service_body(ctx.db, snap_2_rs_1.id, 4, 'test', 'test')
    crud.create_service_body(ctx.db, snap_1_rs_2.id, 5, 'test', 'test')
    crud.create_service_body(ctx.db, snap_1_rs_2.id, 6, 'test', 'test')
    crud.create_service_body(ctx.db, snap_2_rs_2.id, 7, 'test', 'test')
    crud.create_service_body(ctx.db, snap_2_rs_2.id, 8, 'test', 'test')

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots/{str(snap_1_rs_1.created_at.date())}/servicebodies")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (1, 2)

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots/{str(snap_2_rs_1.created_at.date())}/servicebodies")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (3, 4)

    response = ctx.client.get(f"/rootservers/{rs_2.id}/snapshots/{str(snap_1_rs_2.created_at.date())}/servicebodies")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (5, 6)

    response = ctx.client.get(f"/rootservers/{rs_2.id}/snapshots/{str(snap_2_rs_2.created_at.date())}/servicebodies")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (7, 8)
