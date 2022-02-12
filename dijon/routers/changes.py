from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from dijon import crud, schemas, snapshot
from dijon.dependencies import Context


router = APIRouter()


@router.get("/rootservers/{root_server_id}/meetings/changes", response_model=schemas.MeetingChangesResponse, status_code=HTTP_200_OK)
def list_meeting_changes(
    root_server_id: int,
    start_date: date,
    end_date: Optional[date] = None,
    service_body_bmlt_ids: Optional[list[int]] = Query(None),
    ctx: Context = Depends()
):
    # TODO write tests
    if end_date is None:
        end_date = datetime.utcnow().date()

    if end_date <= start_date:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Start date must be before end date")

    old_snapshot = crud.get_nearest_snapshot_by_date(ctx.db, root_server_id, start_date)
    if not old_snapshot:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No snapshots found on or before start date")

    new_snapshot = crud.get_nearest_snapshot_by_date(ctx.db, root_server_id, end_date)
    if new_snapshot == old_snapshot:
        events = []
    else:
        events = snapshot.diff(ctx.db, old_snapshot.id, new_snapshot.id, service_body_bmlt_ids)

    return schemas.MeetingChangesResponse(
        start_date=old_snapshot.created_at.date(),
        end_date=new_snapshot.created_at.date(),
        events=events,
    )
