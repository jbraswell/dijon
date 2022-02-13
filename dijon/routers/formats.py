from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from dijon import crud, snapshot
from dijon.dependencies import Context
from dijon.snapshot import structs


router = APIRouter()


@router.get("/rootservers/{root_server_id}/snapshots/{date}/formats", response_model=list[structs.Format], status_code=HTTP_200_OK)
def list_snapshot_formats(
    root_server_id: int,
    date: date,
    ctx: Context = Depends()
):
    snap = crud.get_snapshot_by_date(ctx.db, root_server_id, date)
    if not snap:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No snapshots found on date")

    return snapshot.get_formats(ctx.db, snap.id)
