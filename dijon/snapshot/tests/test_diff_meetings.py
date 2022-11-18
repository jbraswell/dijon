from datetime import time, timedelta
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.snapshot import structs
from dijon.snapshot.cache import NawsCodeCache
from dijon.snapshot.diff import Data, diff_snapshots


def create_root_server(db: Session) -> models.RootServer:
    return crud.create_root_server(db, "root name", "https://blah/main_server/", True)


def create_snapshot(db: Session, root_server: models.RootServer) -> models.Snapshot:
    return crud.create_snapshot(db, root_server)


def create_service_body(db: Session, snapshot_id: int, bmlt_id: int, parent_id: int = None) -> models.ServiceBody:
    return crud.create_service_body(db, snapshot_id, bmlt_id, f"sb name {bmlt_id}", "AS", parent_id=parent_id)


def create_format(db: Session, snapshot: models.Snapshot, bmlt_id: int, key_string: str, name: str, world_id: str = None) -> models.Format:
    return crud.create_format(db, snapshot.id, bmlt_id, key_string=key_string, name=name, world_id=world_id)


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


def create_meeting(db: Session, formats: list[models.Format], **kwargs):
    db_meeting = models.Meeting(**kwargs)
    db.add(db_meeting)
    for format in formats:
        db_meeting_format = models.MeetingFormat(meeting=db_meeting, format=format)
        db.add(db_meeting_format)
    db.flush()
    db.refresh(db_meeting)
    return db_meeting


@pytest.fixture
def root_server(db: Session) -> models.RootServer:
    return create_root_server(db)


@pytest.fixture
def snap_1(db: Session, root_server: models.RootServer) -> models.Snapshot:
    return create_snapshot(db, root_server)


@pytest.fixture
def snap_2(db: Session, root_server: models.RootServer) -> models.Snapshot:
    return create_snapshot(db, root_server)


@pytest.fixture
def sb_1_snap_1(db: Session, snap_1: models.Snapshot) -> models.ServiceBody:
    return create_service_body(db, snap_1.id, 1)


@pytest.fixture
def sb_2_snap_1(db: Session, sb_1_snap_1: models.ServiceBody) -> models.ServiceBody:
    return create_service_body(db, sb_1_snap_1.snapshot_id, 2, parent_id=sb_1_snap_1.id)


@pytest.fixture
def sb_1_snap_2(db: Session, snap_2: models.Snapshot) -> models.ServiceBody:
    return create_service_body(db, snap_2.id, 1)


@pytest.fixture
def sb_2_snap_2(db: Session, sb_1_snap_2: models.ServiceBody) -> models.ServiceBody:
    return create_service_body(db, sb_1_snap_2.snapshot_id, 2, parent_id=sb_1_snap_2.id)


@pytest.fixture
def fmt_123_snap_1(db: Session, snap_1: models.Snapshot) -> models.Format:
    return create_format(db, snap_1, 123, "AA", "A A")


@pytest.fixture
def fmt_123_snap_2(db: Session, snap_2: models.Snapshot) -> models.Format:
    return create_format(db, snap_2, 123, "AA", "A A")


@pytest.fixture
def mtg_1_snap_1(db: Session, snap_1: models.Snapshot, sb_1_snap_1: models.ServiceBody, fmt_123_snap_1: models.Format) -> models.Meeting:
    return create_meeting(db, [fmt_123_snap_1], **get_meeting_kwargs(snap_1, sb_1_snap_1, 1))


@pytest.fixture
def mtg_2_snap_1(db: Session, snap_1: models.Snapshot, sb_1_snap_1: models.ServiceBody, fmt_123_snap_1: models.Format) -> models.Meeting:
    return create_meeting(db, [fmt_123_snap_1], **get_meeting_kwargs(snap_1, sb_1_snap_1, 2))


@pytest.fixture
def mtg_1_snap_2(db: Session, snap_2: models.Snapshot, sb_1_snap_2: models.ServiceBody, fmt_123_snap_2: models.Format) -> models.Meeting:
    return create_meeting(db, [fmt_123_snap_2], **get_meeting_kwargs(snap_2, sb_1_snap_2, 1))


@pytest.fixture
def mtg_2_snap_2(db: Session, snap_2: models.Snapshot, sb_1_snap_2: models.ServiceBody, fmt_123_snap_2: models.Format) -> models.Meeting:
    return create_meeting(db, [fmt_123_snap_2], **get_meeting_kwargs(snap_2, sb_1_snap_2, 2))


@pytest.fixture
def cache(db: Session, root_server: models.RootServer) -> NawsCodeCache:
    return NawsCodeCache(db, root_server)


def test_diff_sb_filter(db: Session, mtg_1_snap_1, mtg_1_snap_2, mtg_2_snap_2):
    old_snapshot_id = mtg_1_snap_1.snapshot_id
    new_snapshot_id = mtg_1_snap_2.snapshot_id
    events = diff_snapshots(db, old_snapshot_id, new_snapshot_id)
    assert len(events) == 1

    service_body_bmlt_id = mtg_1_snap_1.service_body.bmlt_id
    events = diff_snapshots(db, old_snapshot_id, new_snapshot_id, service_body_bmlt_ids=[service_body_bmlt_id])
    assert len(events) == 1

    events = diff_snapshots(db, old_snapshot_id, new_snapshot_id, service_body_bmlt_ids=[10000])
    assert len(events) == 0


def test_diff_no_changes(mtg_1_snap_1, mtg_1_snap_2, cache):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    assert data.diff() == []


def test_diff_meeting_sb_filter(mtg_1_snap_1, mtg_1_snap_2, mtg_2_snap_2, cache):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2, mtg_2_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == structs.MeetingEventType.MEETING_CREATED
    assert event.old_meeting is None
    assert event.new_meeting is not None


def test_diff_meeting_created(mtg_1_snap_1, mtg_1_snap_2, mtg_2_snap_2, cache):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2, mtg_2_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == structs.MeetingEventType.MEETING_CREATED
    assert event.old_meeting is None
    assert event.new_meeting is not None


def test_diff_meeting_deleted(mtg_1_snap_1, mtg_2_snap_1, mtg_1_snap_2, cache):
    data = Data([mtg_1_snap_1, mtg_2_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == structs.MeetingEventType.MEETING_DELETED
    assert event.old_meeting is not None
    assert event.new_meeting is None


def test_diff_meeting_updated_name(db: Session, mtg_1_snap_1,  mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.name = "changed"
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.name == "changed"
    assert event.changed_fields == ["name"]


def test_diff_meeting_updated_day(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.day = models.DayOfWeekEnum.TUESDAY
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.day == models.DayOfWeekEnum.TUESDAY
    assert event.changed_fields == ["day"]


def test_diff_meeting_updated_service_body(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    new_sb = create_service_body(db, mtg_1_snap_2.snapshot_id, 100)
    mtg_1_snap_2.service_body_id = new_sb.id
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.service_body_bmlt_id == new_sb.bmlt_id
    assert event.changed_fields == ["service_body_bmlt_id"]


def test_diff_meeting_updated_venue_type(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.venue_type = models.VenueTypeEnum.HYBRID
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.venue_type == models.VenueTypeEnum.HYBRID
    assert event.changed_fields == ["venue_type"]


def test_diff_meeting_updated_start_time(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.start_time = time(hour=23)
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.start_time == time(hour=23)
    assert event.changed_fields == ["start_time"]


def test_diff_meeting_updated_duration(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.duration = timedelta(hours=2)
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.duration == timedelta(hours=2)
    assert event.changed_fields == ["duration"]


def test_diff_meeting_updated_latitude(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.latitude = Decimal("52.123")
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.latitude == Decimal("52.123")
    assert event.changed_fields == ["latitude"]


def test_diff_meeting_updated_longitude(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.longitude = Decimal("52.123")
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.longitude == Decimal("52.123")
    assert event.changed_fields == ["longitude"]


def test_diff_meeting_updated_published(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.published = False
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.published is False
    assert event.changed_fields == ["published"]


def test_diff_meeting_updated_exclude_world_id_updates(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    mtg_1_snap_2.world_id = 'this is a change'
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache, exclude_world_id_updates=True)
    events = data.diff()
    assert len(events) == 0


@pytest.mark.parametrize(
    "field_name",
    [
        "time_zone",
        "world_id",
        "location_text",
        "location_info",
        "location_street",
        "location_city_subsection",
        "location_neighborhood",
        "location_municipality",
        "location_sub_province",
        "location_province",
        "location_postal_code_1",
        "location_nation",
        "train_lines",
        "bus_lines",
        "comments",
        "virtual_meeting_link",
        "phone_meeting_number",
        "virtual_meeting_additional_info",
    ]
)
def test_diff_meeting_updated_optional_text_fields(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache, field_name: str):
    for new_value in ("changed", None):
        setattr(mtg_1_snap_2, field_name, new_value)
        db.add(mtg_1_snap_2)
        db.flush()
        db.refresh(mtg_1_snap_2)

        data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
        events = data.diff()
        assert len(events) == 1
        event = events[0]
        assert getattr(event.new_meeting, field_name) == new_value
        assert event.changed_fields == [field_name]


def test_diff_meeting_naws_code(db: Session, mtg_1_snap_1, mtg_1_snap_2, cache):
    naws_code = crud.create_meeting_naws_code(db, mtg_1_snap_1.snapshot.root_server_id, mtg_1_snap_1.bmlt_id, "test")
    mtg_1_snap_1.name = "changed"
    db.add(mtg_1_snap_1)
    db.flush()

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    event = events[0]
    assert event.old_meeting.naws_code_override == "test"
    assert event.new_meeting.naws_code_override == "test"

    crud.delete_meeting_naws_code(db, naws_code.id)
    cache.clear()
    events = data.diff()
    event = events[0]
    assert event.old_meeting.naws_code_override is None
    assert event.new_meeting.naws_code_override is None


def test_diff_meeting_updated_format_removed(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    db.query(models.MeetingFormat).filter(models.MeetingFormat.meeting == mtg_1_snap_2).delete()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.old_meeting.format_bmlt_ids == [mtg_1_snap_1.meeting_formats[0].format.bmlt_id]
    assert event.new_meeting.format_bmlt_ids == []
    assert event.changed_fields == ["format_bmlt_ids"]


def test_diff_meeting_updated_format_added(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, cache):
    db.query(models.MeetingFormat).filter(models.MeetingFormat.meeting == mtg_1_snap_1).delete()
    db.refresh(mtg_1_snap_1)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2], cache)
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.old_meeting.format_bmlt_ids == []
    assert event.new_meeting.format_bmlt_ids == [mtg_1_snap_2.meeting_formats[0].format.bmlt_id]
    assert event.changed_fields == ["format_bmlt_ids"]


def test_snapshot_struct_service_body_bmlt_id(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.bmlt_id = 123
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.bmlt_id == 123


def test_snapshot_struct_service_body_parent_bmlt_id(sb_1_snap_1: models.ServiceBody, sb_2_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.parent_bmlt_id is None

    sb = structs.ServiceBody.from_db_obj(sb_2_snap_1, cache)
    assert sb.parent_bmlt_id == sb_1_snap_1.bmlt_id


def test_snapshot_struct_service_body_name(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.name = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.name == "changed"


def test_snapshot_struct_service_body_type(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.type = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.type == "changed"


def test_snapshot_struct_service_body_description(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.description = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.description == "changed"

    sb_1_snap_1.description = None
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.description is None


def test_snapshot_struct_service_body_url(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.url = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.url == "changed"

    sb_1_snap_1.url = None
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.url is None


def test_snapshot_struct_service_body_helpline(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.helpline = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.helpline == "changed"

    sb_1_snap_1.helpline = None
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.helpline is None


def test_snapshot_struct_service_body_world_id(sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    sb_1_snap_1.world_id = "changed"
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.world_id == "changed"

    sb_1_snap_1.world_id = None
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.world_id is None


def test_snapshot_struct_service_body_naws_code(db: Session, sb_1_snap_1: models.ServiceBody, cache: NawsCodeCache):
    naws_code = crud.create_service_body_naws_code(db, sb_1_snap_1.snapshot.root_server_id, sb_1_snap_1.bmlt_id, "test")
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.naws_code_override == "test"

    crud.delete_service_body_naws_code(db, naws_code.id)
    cache.clear()
    sb = structs.ServiceBody.from_db_obj(sb_1_snap_1, cache)
    assert sb.naws_code_override is None


def test_snapshot_struct_format_bmlt_id(fmt_123_snap_1: models.Format, cache: NawsCodeCache):
    fmt_123_snap_1.bmlt_id = 123
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.bmlt_id == 123


def test_snapshot_struct_format_key_string(fmt_123_snap_1: models.Format, cache: NawsCodeCache):
    fmt_123_snap_1.key_string = "changed"
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.key_string == "changed"


def test_snapshot_struct_format_name(fmt_123_snap_1: models.Format, cache: NawsCodeCache):
    fmt_123_snap_1.name = "changed"
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.name == "changed"

    fmt_123_snap_1.name = None
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.name is None


def test_snapshot_struct_format_world_id(fmt_123_snap_1: models.Format, cache: NawsCodeCache):
    fmt_123_snap_1.world_id = "changed"
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.world_id == "changed"

    fmt_123_snap_1.world_id = None
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.world_id is None


def test_snapshot_struct_format_naws_code(db: Session, fmt_123_snap_1: models.Format, cache: NawsCodeCache):
    naws_code = crud.create_format_naws_code(db, fmt_123_snap_1.snapshot.root_server_id, fmt_123_snap_1.bmlt_id, "test")
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.naws_code_override == "test"

    crud.delete_format_naws_code(db, naws_code.id)
    cache.clear()
    fmt = structs.Format.from_db_obj(fmt_123_snap_1, cache)
    assert fmt.naws_code_override is None


def test_get_child_service_body_bmlt_ids(db: Session, snap_1: models.Snapshot):
    sb_1 = create_service_body(db, snap_1.id, 1)
    sb_1_1 = create_service_body(db, snap_1.id, 2, sb_1.id)
    sb_1_1_1 = create_service_body(db, snap_1.id, 3, sb_1_1.id)
    sb_1_2 = create_service_body(db, snap_1.id, 4, sb_1.id)
    sb_2 = create_service_body(db, snap_1.id, 5)

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_1.bmlt_id])
    assert len(child_bmlt_ids) == 4
    assert sorted(child_bmlt_ids) == sorted([sb_1.bmlt_id, sb_1_1.bmlt_id, sb_1_1_1.bmlt_id, sb_1_2.bmlt_id])

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_1_1.bmlt_id])
    assert len(child_bmlt_ids) == 2
    assert sorted(child_bmlt_ids) == sorted([sb_1_1.bmlt_id, sb_1_1_1.bmlt_id])

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_1_1_1.bmlt_id])
    assert len(child_bmlt_ids) == 1
    assert sorted(child_bmlt_ids) == sorted([sb_1_1_1.bmlt_id])

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_2.bmlt_id])
    assert len(child_bmlt_ids) == 1
    assert sorted(child_bmlt_ids) == sorted([sb_2.bmlt_id])


def test_get_child_service_body_bmlt_ids_circular(db: Session, snap_1: models.Snapshot):
    sb_1 = create_service_body(db, snap_1.id, 1)
    sb_2 = create_service_body(db, snap_1.id, 5, sb_1.id)
    sb_1.parent_id = sb_2.id
    db.add(sb_1)
    db.flush()
    db.refresh(sb_1)

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_1.bmlt_id])
    assert len(child_bmlt_ids) == 2
    assert sorted(child_bmlt_ids) == sorted([sb_1.bmlt_id, sb_2.bmlt_id])

    child_bmlt_ids = crud.get_child_service_body_bmlt_ids(db, snap_1.id, [sb_2.bmlt_id])
    assert len(child_bmlt_ids) == 2
    assert sorted(child_bmlt_ids) == sorted([sb_1.bmlt_id, sb_2.bmlt_id])
