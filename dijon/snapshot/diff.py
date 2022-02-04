import dataclasses
from datetime import time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic.dataclasses import dataclass
from sqlalchemy.orm import Session

from dijon import crud, models


class MeetingEventType(Enum):
    MEETING_DELETED = "MeetingDeleted"
    MEETING_CREATED = "MeetingCreated"
    MEETING_UPDATED = "MeetingUpdated"


class ORMMode:
    orm_mode = True


@dataclass
class DiffMeeting:
    bmlt_id: int
    name: str
    day: models.DayOfWeekEnum
    service_body_bmlt_id: int
    venue_type: models.VenueTypeEnum
    start_time: time
    duration: timedelta
    time_zone: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    published: bool
    world_id: Optional[str]
    location_text: Optional[str]
    location_info: Optional[str]
    location_street: Optional[str]
    location_city_subsection: Optional[str]
    location_neighborhood: Optional[str]
    location_municipality: Optional[str]
    location_sub_province: Optional[str]
    location_province: Optional[str]
    location_postal_code_1: Optional[str]
    location_nation: Optional[str]
    train_lines: Optional[str]
    bus_lines: Optional[str]
    comments: Optional[str]
    virtual_meeting_link: Optional[str]
    phone_meeting_number: Optional[str]
    virtual_meeting_additional_info: Optional[str]
    format_bmlt_ids: list[int]


@dataclass(config=ORMMode)
class ServiceBody:
    bmlt_id: int
    parent_bmlt_id: Optional[int]
    name: str
    type: str
    description: Optional[str]
    url: Optional[str]
    helpline: Optional[str]
    world_id: Optional[str]
    naws_code_override: Optional[str]


@dataclass(config=ORMMode)
class Format:
    bmlt_id: int
    key_string: str
    name: Optional[str]
    world_id: Optional[str]
    naws_code_override: Optional[str]


@dataclass(config=ORMMode)
class Meeting(DiffMeeting):
    naws_code_override: Optional[str]
    service_body: ServiceBody
    formats: list[Format]


@dataclass(config=ORMMode)
class MeetingEvent:
    event_type: MeetingEventType
    old_meeting: Optional[Meeting]
    new_meeting: Optional[Meeting]
    changed_fields: list[str]


class Data:
    def __init__(self, old: list[models.Meeting], new: list[models.Meeting]):
        self.old_db_meetings = old
        self.new_db_meetings = new
        self.old_db_meetings_by_id = {m.bmlt_id: m for m in self.old_db_meetings}
        self.new_db_meetings_by_id = {m.bmlt_id: m for m in self.new_db_meetings}
        self.old_diff_meetings = self.db_meetings_to_diff_meetings(self.old_db_meetings)
        self.new_diff_meetings = self.db_meetings_to_diff_meetings(self.new_db_meetings)
        self.old_diff_meetings_by_id = {m.bmlt_id: m for m in self.old_diff_meetings}
        self.new_diff_meetings_by_id = {m.bmlt_id: m for m in self.new_diff_meetings}

    @classmethod
    def db_meetings_to_diff_meetings(cls, db_meetings: list[models.Meeting]) -> list[DiffMeeting]:
        return [cls.db_meeting_to_diff_meeting(m) for m in db_meetings]

    @staticmethod
    def db_meeting_to_diff_meeting(db_meeting: models.Meeting) -> DiffMeeting:
        return DiffMeeting(
            bmlt_id=db_meeting.bmlt_id,
            name=db_meeting.name,
            day=db_meeting.day,
            service_body_bmlt_id=db_meeting.service_body.bmlt_id,
            venue_type=db_meeting.venue_type,
            start_time=db_meeting.start_time,
            duration=db_meeting.duration,
            time_zone=db_meeting.time_zone,
            latitude=db_meeting.latitude,
            longitude=db_meeting.longitude,
            published=db_meeting.published,
            world_id=db_meeting.world_id,
            location_text=db_meeting.location_text,
            location_info=db_meeting.location_info,
            location_street=db_meeting.location_street,
            location_city_subsection=db_meeting.location_city_subsection,
            location_neighborhood=db_meeting.location_neighborhood,
            location_municipality=db_meeting.location_municipality,
            location_sub_province=db_meeting.location_sub_province,
            location_province=db_meeting.location_province,
            location_postal_code_1=db_meeting.location_postal_code_1,
            location_nation=db_meeting.location_nation,
            train_lines=db_meeting.train_lines,
            bus_lines=db_meeting.bus_lines,
            comments=db_meeting.comments,
            virtual_meeting_link=db_meeting.virtual_meeting_link,
            phone_meeting_number=db_meeting.phone_meeting_number,
            virtual_meeting_additional_info=db_meeting.virtual_meeting_additional_info,
            format_bmlt_ids=sorted([mf.format.bmlt_id for mf in db_meeting.meeting_formats])
        )

    def db_service_body_to_service_body(self, db_service_body: models.ServiceBody) -> ServiceBody:
        return ServiceBody(
            bmlt_id=db_service_body.bmlt_id,
            parent_bmlt_id=db_service_body.parent.bmlt_id if db_service_body.parent else None,
            name=db_service_body.name,
            type=db_service_body.type,
            description=db_service_body.description,
            url=db_service_body.url,
            helpline=db_service_body.helpline,
            world_id=db_service_body.world_id,
            naws_code_override=db_service_body.naws_code
        )

    def db_format_to_format(self, db_format: models.Format) -> Format:
        return Format(
            bmlt_id=db_format.bmlt_id,
            key_string=db_format.key_string,
            name=db_format.name,
            world_id=db_format.world_id,
            naws_code_override=db_format.naws_code
        )

    def diff_meeting_to_meeting(self, diff_meeting: DiffMeeting, db_meeting: models.Meeting):
        naws_code_override = db_meeting.naws_code if db_meeting.naws_code else None
        service_body = self.db_service_body_to_service_body(db_meeting.service_body) if db_meeting.service_body else None
        kwargs = dataclasses.asdict(diff_meeting)
        # TODO test naws_code_override
        kwargs["naws_code_override"] = naws_code_override
        # TODO test all service_body fields
        kwargs["service_body"] = service_body
        # TODO test all formats fields
        kwargs["formats"] = [self.db_format_to_format(mf.format) for mf in db_meeting.meeting_formats]
        return Meeting(**kwargs)

    def create_created_event(self, meeting: Meeting) -> MeetingEvent:
        return MeetingEvent(
            event_type=MeetingEventType.MEETING_CREATED,
            old_meeting=None,
            new_meeting=meeting,
            changed_fields=[]
        )

    def get_created_events(self):
        created_events = []
        for diff_meeting in self.new_diff_meetings:
            if diff_meeting.bmlt_id not in self.old_diff_meetings_by_id:
                db_meeting = self.new_db_meetings_by_id[diff_meeting.bmlt_id]
                meeting = self.diff_meeting_to_meeting(diff_meeting, db_meeting)
                event = self.create_created_event(meeting)
                created_events.append(event)
        return created_events

    def create_deleted_event(self, meeting: Meeting) -> MeetingEvent:
        return MeetingEvent(
            event_type=MeetingEventType.MEETING_DELETED,
            old_meeting=meeting,
            new_meeting=None,
            changed_fields=[]
        )

    def get_deleted_events(self):
        deleted_events = []
        for diff_meeting in self.old_diff_meetings:
            if diff_meeting.bmlt_id not in self.new_diff_meetings_by_id:
                db_meeting = self.old_db_meetings_by_id[diff_meeting.bmlt_id]
                meeting = self.diff_meeting_to_meeting(diff_meeting, db_meeting)
                event = self.create_deleted_event(meeting)
                deleted_events.append(event)
        return deleted_events

    def create_updated_event(self, old_meeting: Meeting, new_meeting: Meeting, changed_fields: list[str]) -> MeetingEvent:
        return MeetingEvent(
            event_type=MeetingEventType.MEETING_UPDATED,
            old_meeting=old_meeting,
            new_meeting=new_meeting,
            changed_fields=changed_fields
        )

    def get_changed_fields(self, old_meeting: DiffMeeting, new_meeting: DiffMeeting) -> list[str]:
        changed_fields = []
        for field in dataclasses.fields(old_meeting):
            if getattr(old_meeting, field.name) != getattr(new_meeting, field.name):
                changed_fields.append(field.name)
        return changed_fields

    def get_updated_events(self):
        updated_events = []
        for diff_meeting in self.old_diff_meetings:
            if diff_meeting.bmlt_id in self.new_diff_meetings_by_id:
                new_diff_meeting = self.new_diff_meetings_by_id[diff_meeting.bmlt_id]
                if diff_meeting != new_diff_meeting:
                    changed_fields = self.get_changed_fields(diff_meeting, new_diff_meeting)
                    db_meeting = self.old_db_meetings_by_id[diff_meeting.bmlt_id]
                    new_db_meeting = self.new_db_meetings_by_id[new_diff_meeting.bmlt_id]
                    meeting = self.diff_meeting_to_meeting(diff_meeting, db_meeting)
                    new_meeting = self.diff_meeting_to_meeting(new_diff_meeting, new_db_meeting)
                    event = self.create_updated_event(meeting, new_meeting, changed_fields)
                    updated_events.append(event)
        return updated_events

    def diff(self) -> list[MeetingEvent]:
        events = self.get_created_events()
        events.extend(self.get_updated_events())
        events.extend(self.get_deleted_events())
        return events


def diff_snapshots(db: Session, old_snapshot_id: int, new_snapshot_id: int, service_body_bmlt_ids: Optional[list[int]] = None) -> list[MeetingEvent]:
    old = crud.get_meetings_for_snapshot(db, old_snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    new = crud.get_meetings_for_snapshot(db, new_snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    data = Data(old, new)
    return data.diff()
