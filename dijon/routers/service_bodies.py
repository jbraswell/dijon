from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from dijon import crud, snapshot
from dijon.dependencies import Context
from dijon.snapshot import structs


router = APIRouter()


@router.get("/rootservers/{root_server_id}/snapshots/{date}/servicebodies", response_model=list[structs.ServiceBody], status_code=HTTP_200_OK)
def list_snapshot_service_bodies(
    root_server_id: int,
    date: date,
    ctx: Context = Depends()
):
    # TODO write tests
    snap = crud.get_snapshot_by_date(ctx.db, root_server_id, date)
    if not snap:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No snapshots found on date")

    return snapshot.get_service_bodies(ctx.db, snap.id)