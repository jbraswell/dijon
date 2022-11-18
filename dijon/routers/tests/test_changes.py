from datetime import timedelta

from dijon import crud
from dijon.conftest import Ctx


def test_meeting_changes_missing_start_before_end(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    response = ctx.client.get(f"/rootservers/{rs.id}/meetings/changes", params={"start_date": "2022-02-01", "end_date": "2021-02-01"})
    assert response.status_code == 400


def test_meeting_changes_missing_start_snapshot(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    response = ctx.client.get(f"/rootservers/{rs.id}/meetings/changes", params={"start_date": "2022-02-01", "end_date": "2022-02-02"})
    assert response.status_code == 404


def test_meeting_changes_missing_end_snapshot(ctx: Ctx):
    rs = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/", True)
    snap = crud.create_snapshot(ctx.db, rs)
    start_date = snap.created_at.date()
    end_date = start_date + timedelta(days=1)
    response = ctx.client.get(f"/rootservers/{rs.id}/meetings/changes", params={"start_date": snap.created_at.date(), "end_date": end_date})
    assert response.status_code == 404
