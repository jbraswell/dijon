import logging
from datetime import time, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field, conint, constr, validator
from pydantic.validators import str_validator
from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.snapshot.cache import SnapshotCache
from dijon.snapshot.diff import diff_snapshots, structs


logger = logging.getLogger(__name__)


class EmptyToNoneStr(str):
    """A str type that converts empty strings to None"""
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield lambda s: None if s == '' else s


class BmltServiceBody(BaseModel):
    id: int
    parent_id: int
    name: constr(min_length=1)
    type: constr(min_length=1)
    description: Optional[EmptyToNoneStr]
    url: Optional[EmptyToNoneStr]
    helpline: Optional[EmptyToNoneStr]
    world_id: Optional[EmptyToNoneStr]

    @classmethod
    def from_url(cls, url: str) -> list["BmltServiceBody"]:
        service_bodies = []
        url = urljoin(url, "client_interface/json/?switcher=GetServiceBodies")
        for raw in get_json(url):
            try:
                obj = cls(**raw)
            except ValueError:
                # TODO report this somewhere
                continue
            else:
                service_bodies.append(obj)
        return service_bodies

    def to_db(self, db: Session, snapshot: models.Snapshot) -> models.ServiceBody:
        return models.ServiceBody(
            snapshot_id=snapshot.id,
            bmlt_id=self.id,
            parent_id=None,
            name=self.name,
            type=self.type,
            description=self.description,
            url=self.url,
            helpline=self.helpline,
            world_id=self.world_id
        )


class BmltFormat(BaseModel):
    id: int
    key_string: constr(min_length=1)
    name_string: Optional[EmptyToNoneStr]
    world_id: Optional[EmptyToNoneStr]

    @classmethod
    def from_url(cls, url: str) -> list["BmltFormat"]:
        formats = []
        url = urljoin(url, "client_interface/json/?switcher=GetFormats")
        for raw in get_json(url):
            try:
                obj = cls(**raw)
            except ValueError:
                # TODO report this somewhere
                continue
            else:
                formats.append(obj)
        return formats

    def to_db(self, db: Session, snapshot: models.Snapshot) -> models.Format:
        return models.Format(
            snapshot_id=snapshot.id,
            bmlt_id=self.id,
            key_string=self.key_string,
            name=self.name_string,
            world_id=self.world_id
        )


class BmltMeeting(BaseModel):
    id_bigint: int
    meeting_name: constr(min_length=1)
    weekday_tinyint: conint(ge=1, le=7)
    worldid_mixed: Optional[EmptyToNoneStr]
    service_body_bigint: int
    start_time: time
    duration_time: timedelta
    venue_type: Optional[conint(ge=1, le=3)]
    time_zone: Optional[EmptyToNoneStr]
    format_shared_id_list: Optional[list[int]] = Field(default_factory=list)
    longitude: Optional[Decimal]
    latitude: Optional[Decimal]
    comments: Optional[EmptyToNoneStr]
    virtual_meeting_additional_info: Optional[EmptyToNoneStr]
    location_city_subsection: Optional[EmptyToNoneStr]
    virtual_meeting_link: Optional[EmptyToNoneStr]
    phone_meeting_number: Optional[EmptyToNoneStr]
    location_nation: Optional[EmptyToNoneStr]
    location_postal_code_1: Optional[EmptyToNoneStr]
    location_province: Optional[EmptyToNoneStr]
    location_sub_province: Optional[EmptyToNoneStr]
    location_municipality: Optional[EmptyToNoneStr]
    location_neighborhood: Optional[EmptyToNoneStr]
    location_street: Optional[EmptyToNoneStr]
    location_info: Optional[EmptyToNoneStr]
    location_text: Optional[EmptyToNoneStr]
    bus_lines: Optional[EmptyToNoneStr]
    train_lines: Optional[EmptyToNoneStr]
    published: bool

    @classmethod
    def from_url(cls, url: str, bmlt_service_bodies: list[BmltServiceBody]) -> list["BmltMeeting"]:
        valid_sb_ids = {sb.id for sb in bmlt_service_bodies}
        meetings = []
        url = urljoin(url, "client_interface/json/?switcher=GetSearchResults&advanced_published=0")
        for raw in get_json(url):
            try:
                obj = cls(**raw)
                if obj.service_body_bigint not in valid_sb_ids:
                    continue
            except ValueError:
                # TODO report this somewhere
                continue
            else:
                meetings.append(obj)
        return meetings

    def to_db(self, db: Session, cache: SnapshotCache) -> tuple[models.Meeting, list[models.MeetingFormat]]:
        service_body = cache.get_service_body(self.service_body_bigint)
        if not service_body:
            raise ValueError("invalid service body")

        db_meeting = models.Meeting(
            snapshot_id=cache.snapshot.id,
            bmlt_id=self.id_bigint,
            name=self.meeting_name,
            day=models.DayOfWeekEnum(self.weekday_tinyint),
            service_body_id=service_body.id,
            venue_type=models.VenueTypeEnum(self.venue_type) if self.venue_type else models.VenueTypeEnum.NONE,
            start_time=self.start_time,
            duration=self.duration_time,
            time_zone=self.time_zone,
            latitude=self.latitude,
            longitude=self.longitude,
            published=self.published,
            world_id=self.worldid_mixed,
            location_text=self.location_text,
            location_info=self.location_info,
            location_street=self.location_street,
            location_city_subsection=self.location_city_subsection,
            location_neighborhood=self.location_neighborhood,
            location_municipality=self.location_municipality,
            location_sub_province=self.location_sub_province,
            location_province=self.location_province,
            location_postal_code_1=self.location_postal_code_1,
            location_nation=self.location_nation,
            train_lines=self.train_lines,
            bus_lines=self.bus_lines,
            comments=self.comments,
            virtual_meeting_link=self.virtual_meeting_link,
            phone_meeting_number=self.phone_meeting_number,
            virtual_meeting_additional_info=self.virtual_meeting_additional_info
        )

        db_formats = crud.get_formats_by_bmlt_ids(db, cache.snapshot.id, self.format_shared_id_list)
        db_meeting_formats = [models.MeetingFormat(meeting=db_meeting, format=db_format) for db_format in db_formats]
        return db_meeting, db_meeting_formats

    @validator("format_shared_id_list", pre=True)
    def format_shared_id_list_pre(cls, v):
        if v is None:
            return []
        if not isinstance(v, str):
            raise ValueError()
        if v == "":
            return []
        return [s.strip() for s in v.split(",")]

    @validator("longitude", pre=True)
    def longitude_pre(cls, v):
        # unset will be unparseable empty string
        try:
            Decimal(v)
        except InvalidOperation:
            return None
        else:
            return v

    @validator("latitude", pre=True)
    def latitude_pre(cls, v):
        # unset will be unparseable empty string
        try:
            Decimal(v)
        except InvalidOperation:
            return None
        else:
            return v

    @validator("venue_type", pre=True)
    def venue_type_pre(cls, v):
        # unset venue_type will be unparseable empty string
        try:
            return int(v)
        except ValueError:
            return None


def get_json(url: str) -> list[Any]:
    # This is just a random user agent that doesn't seem to get blocked by webhosts
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0 +dijon'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Unexpected status code {response.status_code} GET {url}")
    return response.json()


def create_snapshot(db: Session, root_server: models.RootServer):
    logger.info(f"creating snapshot for {root_server.id}:{root_server.url}...")
    snapshot = crud.create_snapshot(db, root_server)

    logger.info("getting service bodies...")
    bmlt_service_bodies = BmltServiceBody.from_url(root_server.url)
    logger.info(f"saving {len(bmlt_service_bodies)} service bodies...")
    save_service_bodies(db, snapshot, bmlt_service_bodies)

    logger.info("getting formats...")
    bmlt_formats = BmltFormat.from_url(root_server.url)
    logger.info(f"saving {len(bmlt_formats)} formats...")
    save_formats(db, snapshot, bmlt_formats)

    logger.info("getting meetings...")
    bmlt_meetings = BmltMeeting.from_url(root_server.url, bmlt_service_bodies)
    logger.info(f"saving {len(bmlt_meetings)} meetings...")
    save_meetings(db, snapshot, bmlt_meetings)

    prev_snapshot = crud.get_previous_snapshot(db, snapshot.id)
    if prev_snapshot:
        update_meetings_last_changed(db, snapshot, prev_snapshot)


def save_service_bodies(db: Session, snapshot: models.Snapshot, bmlt_service_bodies: list[BmltServiceBody]):
    for bmlt_sb in bmlt_service_bodies:
        db_sb = bmlt_sb.to_db(db, snapshot)
        db.add(db_sb)
    db.flush()

    for bmlt_sb in bmlt_service_bodies:
        if bmlt_sb.parent_id:
            db_sb_parent = (
                db.query(models.ServiceBody)
                  .filter(models.ServiceBody.snapshot_id == snapshot.id, models.ServiceBody.bmlt_id == bmlt_sb.parent_id)
                  .first()
            )
            if db_sb_parent:
                (db.query(models.ServiceBody)
                   .filter(models.ServiceBody.snapshot_id == snapshot.id, models.ServiceBody.bmlt_id == bmlt_sb.id)
                   .update({models.ServiceBody.parent_id: db_sb_parent.id}))
    db.flush()


def save_formats(db: Session, snapshot: models.Snapshot, bmlt_formats: list[BmltFormat]):
    for bmlt_format in bmlt_formats:
        db_format = bmlt_format.to_db(db, snapshot)
        db.add(db_format)
    db.flush()


def save_meetings(db: Session, snapshot: models.Snapshot, bmlt_meetings: list[BmltMeeting]):
    cache = SnapshotCache(db, snapshot)
    for bmlt_meeting in bmlt_meetings:
        db_meeting, db_meeting_formats = bmlt_meeting.to_db(db, cache)
        db.add(db_meeting)
        db.add_all(db_meeting_formats)
    db.flush()


def update_meetings_last_changed(db: Session, snapshot: models.Snapshot, prev_snapshot: models.Snapshot):
    meetings_by_bmlt_id = {db_m.bmlt_id: db_m for db_m in crud.get_meetings_for_snapshot(db, snapshot.id)}
    prev_meetings_by_bmlt_id = {db_m.bmlt_id: db_m for db_m in crud.get_meetings_for_snapshot(db, prev_snapshot.id)}

    for event in diff_snapshots(db, prev_snapshot.id, snapshot.id):
        if event.event_type != structs.MeetingEventType.MEETING_DELETED:
            db_meeting = meetings_by_bmlt_id[event.new_meeting.bmlt_id]
            db_meeting.last_changed = snapshot.created_at
            db.add(db_meeting)

    for db_meeting in (m for m in meetings_by_bmlt_id.values() if m.last_changed is None):
        prev_db_meeting = prev_meetings_by_bmlt_id.get(db_meeting.bmlt_id)
        if prev_db_meeting and prev_db_meeting.last_changed is not None:
            db_meeting.last_changed = prev_db_meeting.last_changed
            db.add(db_meeting)

    db.flush()
