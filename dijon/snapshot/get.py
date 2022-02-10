from typing import Optional

from sqlalchemy.orm import Session

from dijon import crud
from dijon.snapshot import structs
from dijon.snapshot.cache import NawsCodeCache


def get_meetings(db: Session, snapshot_id: int, service_body_bmlt_ids: Optional[list[int]] = None) -> list[structs.Meeting]:
    snap = crud.get_snapshot_by_id(db, snapshot_id)
    cache = NawsCodeCache(db, snap.root_server)
    db_meetings = crud.get_meetings_for_snapshot(db, snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    return structs.Meeting.from_db_obj_list(db_meetings, cache)


def get_formats(db: Session, snapshot_id: int) -> list[structs.Format]:
    snap = crud.get_snapshot_by_id(db, snapshot_id)
    cache = NawsCodeCache(db, snap.root_server)
    db_formats = crud.get_formats_for_snapshot(db, snapshot_id)
    return structs.Format.from_db_obj_list(db_formats, cache)


def get_service_bodies(db: Session, snapshot_id: int) -> list[structs.ServiceBody]:
    snap = crud.get_snapshot_by_id(db, snapshot_id)
    cache = NawsCodeCache(db, snap.root_server)
    db_service_bodies = crud.get_service_bodies_for_snapshot(db, snapshot_id)
    return structs.ServiceBody.from_db_obj_list(db_service_bodies, cache)
