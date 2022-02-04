from datetime import time, timedelta
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.snapshot.diff import Data, MeetingEventType, diff_snapshots


def create_root_server(db: Session) -> models.RootServer:
    return crud.create_root_server(db, "root name", "https://blah/main_server/")


def create_snapshot(db: Session, root_server: models.RootServer) -> models.Snapshot:
    return crud.create_snapshot(db, root_server)


def create_service_body(db: Session, snapshot_id: int, bmlt_id: int) -> models.ServiceBody:
    return crud.create_service_body(db, snapshot_id, bmlt_id, f"sb name {bmlt_id}", "AS")


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
        "meeting_naws_code_id": None,
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
def sb_1_snap_2(db: Session, snap_2: models.Snapshot) -> models.ServiceBody:
    return create_service_body(db, snap_2.id, 1)


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


def test_diff_no_changes(mtg_1_snap_1, mtg_1_snap_2):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    assert data.diff() == []


def test_diff_meeting_sb_filter(mtg_1_snap_1, mtg_1_snap_2, mtg_2_snap_2):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2, mtg_2_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == MeetingEventType.MEETING_CREATED
    assert event.old_meeting is None
    assert event.new_meeting is not None


def test_diff_meeting_created(mtg_1_snap_1, mtg_1_snap_2, mtg_2_snap_2):
    data = Data([mtg_1_snap_1], [mtg_1_snap_2, mtg_2_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == MeetingEventType.MEETING_CREATED
    assert event.old_meeting is None
    assert event.new_meeting is not None


def test_diff_meeting_deleted(mtg_1_snap_1, mtg_2_snap_1, mtg_1_snap_2):
    data = Data([mtg_1_snap_1, mtg_2_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.event_type == MeetingEventType.MEETING_DELETED
    assert event.old_meeting is not None
    assert event.new_meeting is None


def test_diff_meeting_updated_name(db: Session, mtg_1_snap_1,  mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.name = "changed"
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.name == "changed"
    assert event.changed_fields == ["name"]


def test_diff_meeting_updated_day(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.day = models.DayOfWeekEnum.TUESDAY
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.day == models.DayOfWeekEnum.TUESDAY
    assert event.changed_fields == ["day"]


def test_diff_meeting_updated_service_body(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    new_sb = create_service_body(db, mtg_1_snap_2.snapshot_id, 100)
    mtg_1_snap_2.service_body_id = new_sb.id
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.service_body_bmlt_id == new_sb.bmlt_id
    assert event.changed_fields == ["service_body_bmlt_id"]


def test_diff_meeting_updated_venue_type(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.venue_type = models.VenueTypeEnum.HYBRID
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.venue_type == models.VenueTypeEnum.HYBRID
    assert event.changed_fields == ["venue_type"]


def test_diff_meeting_updated_start_time(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.start_time = time(hour=23)
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.start_time == time(hour=23)
    assert event.changed_fields == ["start_time"]


def test_diff_meeting_updated_duration(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.duration = timedelta(hours=2)
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.duration == timedelta(hours=2)
    assert event.changed_fields == ["duration"]


def test_diff_meeting_updated_latitude(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.latitude = Decimal("52.123")
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.latitude == Decimal("52.123")
    assert event.changed_fields == ["latitude"]


def test_diff_meeting_updated_longitude(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.longitude = Decimal("52.123")
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.longitude == Decimal("52.123")
    assert event.changed_fields == ["longitude"]


def test_diff_meeting_updated_published(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    mtg_1_snap_2.published = False
    db.add(mtg_1_snap_2)
    db.flush()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.new_meeting.published is False
    assert event.changed_fields == ["published"]


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
def test_diff_meeting_updated_optional_text_fields(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting, field_name: str):
    for new_value in ("changed", None):
        setattr(mtg_1_snap_2, field_name, new_value)
        db.add(mtg_1_snap_2)
        db.flush()
        db.refresh(mtg_1_snap_2)

        data = Data([mtg_1_snap_1], [mtg_1_snap_2])
        events = data.diff()
        assert len(events) == 1
        event = events[0]
        assert getattr(event.new_meeting, field_name) == new_value
        assert event.changed_fields == [field_name]


def test_diff_meeting_updated_format_removed(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    db.query(models.MeetingFormat).filter(models.MeetingFormat.meeting == mtg_1_snap_2).delete()
    db.refresh(mtg_1_snap_2)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.old_meeting.format_bmlt_ids == [mtg_1_snap_1.meeting_formats[0].format.bmlt_id]
    assert event.new_meeting.format_bmlt_ids == []
    assert event.changed_fields == ["format_bmlt_ids"]


def test_diff_meeting_updated_format_added(db: Session, mtg_1_snap_1, mtg_1_snap_2: models.Meeting):
    db.query(models.MeetingFormat).filter(models.MeetingFormat.meeting == mtg_1_snap_1).delete()
    db.refresh(mtg_1_snap_1)

    data = Data([mtg_1_snap_1], [mtg_1_snap_2])
    events = data.diff()
    assert len(events) == 1
    event = events[0]
    assert event.old_meeting.format_bmlt_ids == []
    assert event.new_meeting.format_bmlt_ids == [mtg_1_snap_2.meeting_formats[0].format.bmlt_id]
    assert event.changed_fields == ["format_bmlt_ids"]
