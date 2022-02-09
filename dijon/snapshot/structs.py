from datetime import time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic.dataclasses import dataclass

from dijon import models
from dijon.snapshot.cache import NawsCodeCache


class MeetingEventType(Enum):
    MEETING_DELETED = "MeetingDeleted"
    MEETING_CREATED = "MeetingCreated"
    MEETING_UPDATED = "MeetingUpdated"


class ORMMode:
    orm_mode = True


@dataclass
class DiffableMeeting:
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

    @classmethod
    def from_db_obj_list(cls, db_obj_list: list[models.Meeting]) -> list["DiffableMeeting"]:
        return [cls.from_db_obj(m) for m in db_obj_list]

    @classmethod
    def from_db_obj(cls, db_obj: models.Meeting) -> "DiffableMeeting":
        return cls(
            bmlt_id=db_obj.bmlt_id,
            name=db_obj.name,
            day=db_obj.day,
            service_body_bmlt_id=db_obj.service_body.bmlt_id,
            venue_type=db_obj.venue_type,
            start_time=db_obj.start_time,
            duration=db_obj.duration,
            time_zone=db_obj.time_zone,
            latitude=db_obj.latitude,
            longitude=db_obj.longitude,
            published=db_obj.published,
            world_id=db_obj.world_id,
            location_text=db_obj.location_text,
            location_info=db_obj.location_info,
            location_street=db_obj.location_street,
            location_city_subsection=db_obj.location_city_subsection,
            location_neighborhood=db_obj.location_neighborhood,
            location_municipality=db_obj.location_municipality,
            location_sub_province=db_obj.location_sub_province,
            location_province=db_obj.location_province,
            location_postal_code_1=db_obj.location_postal_code_1,
            location_nation=db_obj.location_nation,
            train_lines=db_obj.train_lines,
            bus_lines=db_obj.bus_lines,
            comments=db_obj.comments,
            virtual_meeting_link=db_obj.virtual_meeting_link,
            phone_meeting_number=db_obj.phone_meeting_number,
            virtual_meeting_additional_info=db_obj.virtual_meeting_additional_info,
            format_bmlt_ids=sorted([mf.format.bmlt_id for mf in db_obj.meeting_formats])
        )


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

    @classmethod
    def from_db_obj(cls, db_obj: models.ServiceBody, cache: NawsCodeCache) -> "ServiceBody":
        naws_code = cache.get_service_body_naws_code(db_obj.bmlt_id)
        return cls(
            bmlt_id=db_obj.bmlt_id,
            parent_bmlt_id=db_obj.parent.bmlt_id if db_obj.parent else None,
            name=db_obj.name,
            type=db_obj.type,
            description=db_obj.description,
            url=db_obj.url,
            helpline=db_obj.helpline,
            world_id=db_obj.world_id,
            naws_code_override=naws_code.code if naws_code else None
        )


@dataclass(config=ORMMode)
class Format:
    bmlt_id: int
    key_string: str
    name: Optional[str]
    world_id: Optional[str]
    naws_code_override: Optional[str]

    @classmethod
    def from_db_obj(cls, db_obj: models.Format, cache: NawsCodeCache) -> "Format":
        naws_code = cache.get_format_naws_code(db_obj.bmlt_id)
        return cls(
            bmlt_id=db_obj.bmlt_id,
            key_string=db_obj.key_string,
            name=db_obj.name,
            world_id=db_obj.world_id,
            naws_code_override=naws_code.code if naws_code else None
        )


@dataclass(config=ORMMode)
class Meeting(DiffableMeeting):
    naws_code_override: Optional[str]
    service_body: ServiceBody
    formats: list[Format]

    @classmethod
    def from_db_obj_list(cls, db_obj_list: list[models.Meeting], cache: NawsCodeCache) -> list["Meeting"]:
        return [cls.from_db_obj(m, cache) for m in db_obj_list]

    @classmethod
    def from_db_obj(cls, db_obj: models.Meeting, cache: NawsCodeCache) -> "Meeting":
        naws_code = cache.get_meeting_naws_code(db_obj.bmlt_id)
        return cls(
            bmlt_id=db_obj.bmlt_id,
            name=db_obj.name,
            day=db_obj.day,
            service_body_bmlt_id=db_obj.service_body.bmlt_id,
            venue_type=db_obj.venue_type,
            start_time=db_obj.start_time,
            duration=db_obj.duration,
            time_zone=db_obj.time_zone,
            latitude=db_obj.latitude,
            longitude=db_obj.longitude,
            published=db_obj.published,
            world_id=db_obj.world_id,
            location_text=db_obj.location_text,
            location_info=db_obj.location_info,
            location_street=db_obj.location_street,
            location_city_subsection=db_obj.location_city_subsection,
            location_neighborhood=db_obj.location_neighborhood,
            location_municipality=db_obj.location_municipality,
            location_sub_province=db_obj.location_sub_province,
            location_province=db_obj.location_province,
            location_postal_code_1=db_obj.location_postal_code_1,
            location_nation=db_obj.location_nation,
            train_lines=db_obj.train_lines,
            bus_lines=db_obj.bus_lines,
            comments=db_obj.comments,
            virtual_meeting_link=db_obj.virtual_meeting_link,
            phone_meeting_number=db_obj.phone_meeting_number,
            virtual_meeting_additional_info=db_obj.virtual_meeting_additional_info,
            format_bmlt_ids=sorted([mf.format.bmlt_id for mf in db_obj.meeting_formats]),
            naws_code_override=naws_code.code if naws_code else None,
            service_body=ServiceBody.from_db_obj(db_obj.service_body, cache) if db_obj.service_body else None,
            formats=[Format.from_db_obj(mf.format, cache) for mf in db_obj.meeting_formats],
        )


@dataclass(config=ORMMode)
class MeetingEvent:
    event_type: MeetingEventType
    old_meeting: Optional[Meeting]
    new_meeting: Optional[Meeting]
    changed_fields: list[str]
