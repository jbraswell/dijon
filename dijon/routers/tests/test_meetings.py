from datetime import time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.conftest import Ctx


def get_meeting_kwargs(snapshot: models.Snapshot = None, service_body: models.ServiceBody = None, bmlt_id: int = None) -> dict[str, Any]:
    return {
        "bmlt_id": bmlt_id,
        "snapshot_id": snapshot.id,
        "name": "meeting name",
        "day": models.DayOfWeekEnum.MONDAY,
        "service_body_id": service_body.id,
        "venue_type": models.VenueTypeEnum.IN_PERSON,
        "start_time": time(hour=12),
        "duration": timedelta(hours=1),
        "time_zone": "America/New_York",
        "latitude": Decimal("-82.8381874"),
        "longitude": Decimal("-82.8381874"),
        "published": True,
        "world_id": "worldid",
        "location_text": "a really nice string",
        "location_info": "a really nice string",
        "location_street": "a really nice string",
        "location_city_subsection": "a really nice string",
        "location_neighborhood": "a really nice string",
        "location_municipality": "a really nice string",
        "location_sub_province": "a really nice string",
        "location_province": "a really nice string",
        "location_postal_code_1": "a really nice string",
        "location_nation": "a really nice string",
        "train_lines": "a really nice string",
        "bus_lines": "a really nice string",
        "comments": "a really nice string",
        "virtual_meeting_link": "a really nice string",
        "phone_meeting_number": "a really nice string",
        "virtual_meeting_additional_info": "a really nice string",
    }


def create_meeting(db: Session, **kwargs):
    db_meeting = models.Meeting(**kwargs)
    db.add(db_meeting)
    db.flush()
    db.refresh(db_meeting)
    return db_meeting


def test_list_snapshot_meetings(ctx: Ctx):
    rs_1 = crud.create_root_server(ctx.db, "root 1", "https://1/main_server/")
    rs_2 = crud.create_root_server(ctx.db, "root 2", "https://1/main_server/")
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
    sb_1_snap_1_rs_1 = crud.create_service_body(ctx.db, snap_1_rs_1.id, 1, 'test', 'test')
    sb_1_snap_1_rs_2 = crud.create_service_body(ctx.db, snap_1_rs_2.id, 1, 'test', 'test')
    sb_1_snap_2_rs_1 = crud.create_service_body(ctx.db, snap_2_rs_1.id, 1, 'test', 'test')
    sb_1_snap_2_rs_2 = crud.create_service_body(ctx.db, snap_2_rs_2.id, 1, 'test', 'test')
    crud.create_service_body(ctx.db, snap_2_rs_2.id, 4, 'test', 'test')
    create_meeting(ctx.db, **get_meeting_kwargs(snap_1_rs_1, sb_1_snap_1_rs_1, 1))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_1_rs_1, sb_1_snap_1_rs_1, 2))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_2_rs_1, sb_1_snap_2_rs_1, 3))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_2_rs_1, sb_1_snap_2_rs_1, 4))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_1_rs_2, sb_1_snap_1_rs_2, 5))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_1_rs_2, sb_1_snap_1_rs_2, 6))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_2_rs_2, sb_1_snap_2_rs_2, 7))
    create_meeting(ctx.db, **get_meeting_kwargs(snap_2_rs_2, sb_1_snap_2_rs_2, 8))

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots/{str(snap_1_rs_1.created_at.date())}/meetings")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (1, 2)

    response = ctx.client.get(f"/rootservers/{rs_1.id}/snapshots/{str(snap_2_rs_1.created_at.date())}/meetings")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (3, 4)

    response = ctx.client.get(f"/rootservers/{rs_2.id}/snapshots/{str(snap_1_rs_2.created_at.date())}/meetings")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (5, 6)

    response = ctx.client.get(f"/rootservers/{rs_2.id}/snapshots/{str(snap_2_rs_2.created_at.date())}/meetings")
    data = response.json()
    assert len(data) == 2
    for sb in data:
        assert sb["bmlt_id"] in (7, 8)
