from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from dijon import crud, snapshot
from dijon.dependencies import Context
from dijon.snapshot import structs


router = APIRouter()


@router.get("/rootservers/{root_server_id}/snapshots/{date}/meetings", response_model=list[structs.Meeting], status_code=HTTP_200_OK)
def list_snapshot_meetings(
    root_server_id: int,
    date: date,
    service_body_bmlt_ids: Optional[list[int]] = Query(None),
    ctx: Context = Depends()
):
    # TODO write tests
    snap = crud.get_snapshot_by_date(ctx.db, root_server_id, date)
    if not snap:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No snapshots found on date")

    return snapshot.get_meetings(ctx.db, snap.id, service_body_bmlt_ids)
