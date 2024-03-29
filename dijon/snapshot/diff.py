import dataclasses
from typing import Optional

from sqlalchemy.orm import Session

from dijon import crud, models
from dijon.snapshot import structs
from dijon.snapshot.cache import NawsCodeCache


class Data:
    def __init__(self, old: list[models.Meeting], new: list[models.Meeting], naws_code_cache: NawsCodeCache, exclude_world_id_updates: bool = False):
        self.old_db_meetings = old
        self.new_db_meetings = new
        self.old_db_meetings_by_id = {m.bmlt_id: m for m in self.old_db_meetings}
        self.new_db_meetings_by_id = {m.bmlt_id: m for m in self.new_db_meetings}
        self.old_diff_meetings = structs.DiffableMeeting.from_db_obj_list(self.old_db_meetings)
        self.new_diff_meetings = structs.DiffableMeeting.from_db_obj_list(self.new_db_meetings)
        self.old_diff_meetings_by_id = {m.bmlt_id: m for m in self.old_diff_meetings}
        self.new_diff_meetings_by_id = {m.bmlt_id: m for m in self.new_diff_meetings}
        self.cache: NawsCodeCache = naws_code_cache
        self.exclude_world_id_updates = exclude_world_id_updates

    def create_created_event(self, meeting: structs.Meeting) -> structs.MeetingEvent:
        return structs.MeetingEvent(
            event_type=structs.MeetingEventType.MEETING_CREATED,
            old_meeting=None,
            new_meeting=meeting,
            changed_fields=[]
        )

    def get_created_events(self):
        created_events = []
        for diff_meeting in self.new_diff_meetings:
            if diff_meeting.bmlt_id not in self.old_diff_meetings_by_id:
                db_meeting = self.new_db_meetings_by_id[diff_meeting.bmlt_id]
                meeting = structs.Meeting.from_db_obj(db_meeting, self.cache)
                event = self.create_created_event(meeting)
                created_events.append(event)
        return created_events

    def create_deleted_event(self, meeting: structs.Meeting) -> structs.MeetingEvent:
        return structs.MeetingEvent(
            event_type=structs.MeetingEventType.MEETING_DELETED,
            old_meeting=meeting,
            new_meeting=None,
            changed_fields=[]
        )

    def get_deleted_events(self):
        deleted_events = []
        for diff_meeting in self.old_diff_meetings:
            if diff_meeting.bmlt_id not in self.new_diff_meetings_by_id:
                db_meeting = self.old_db_meetings_by_id[diff_meeting.bmlt_id]
                meeting = structs.Meeting.from_db_obj(db_meeting, self.cache)
                event = self.create_deleted_event(meeting)
                deleted_events.append(event)
        return deleted_events

    def create_updated_event(self, old_meeting: structs.Meeting, new_meeting: structs.Meeting, changed_fields: list[str]) -> structs.MeetingEvent:
        return structs.MeetingEvent(
            event_type=structs.MeetingEventType.MEETING_UPDATED,
            old_meeting=old_meeting,
            new_meeting=new_meeting,
            changed_fields=changed_fields
        )

    def get_changed_fields(self, old_meeting: structs.DiffableMeeting, new_meeting: structs.DiffableMeeting) -> list[str]:
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
                    if self.exclude_world_id_updates:
                        if len(changed_fields) == 1 and changed_fields[0] == "world_id":
                            continue
                    db_meeting = self.old_db_meetings_by_id[diff_meeting.bmlt_id]
                    new_db_meeting = self.new_db_meetings_by_id[new_diff_meeting.bmlt_id]
                    meeting = structs.Meeting.from_db_obj(db_meeting, self.cache)
                    new_meeting = structs.Meeting.from_db_obj(new_db_meeting, self.cache)
                    event = self.create_updated_event(meeting, new_meeting, changed_fields)
                    updated_events.append(event)
        return updated_events

    def diff(self) -> list[structs.MeetingEvent]:
        events = self.get_created_events()
        events.extend(self.get_updated_events())
        events.extend(self.get_deleted_events())
        return events


def diff_snapshots(db: Session, old_snapshot_id: int, new_snapshot_id: int, service_body_bmlt_ids: Optional[list[int]] = None, exclude_world_id_updates: bool = False) -> list[structs.MeetingEvent]:
    snap = crud.get_snapshot_by_id(db, old_snapshot_id)
    cache = NawsCodeCache(db, snap.root_server)
    if service_body_bmlt_ids is not None:
        unique = set()
        for bmlt_id in crud.get_child_service_body_bmlt_ids(db, old_snapshot_id, service_body_bmlt_ids):
            unique.add(bmlt_id)
        for bmlt_id in crud.get_child_service_body_bmlt_ids(db, new_snapshot_id, service_body_bmlt_ids):
            unique.add(bmlt_id)
        service_body_bmlt_ids = list(unique)
    old = crud.get_meetings_for_snapshot(db, old_snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    new = crud.get_meetings_for_snapshot(db, new_snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    data = Data(old, new, cache, exclude_world_id_updates=exclude_world_id_updates)
    return data.diff()
