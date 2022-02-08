from typing import Optional

from sqlalchemy.orm import Session

from dijon import crud
from dijon.snapshot import structs


def get_meetings(db: Session, snapshot_id: int, service_body_bmlt_ids: Optional[list[int]] = None) -> list[structs.Meeting]:
    db_meetings = crud.get_meetings_for_snapshot(db, snapshot_id, service_body_bmlt_ids=service_body_bmlt_ids)
    return structs.Meeting.from_db_obj_list(db_meetings)
