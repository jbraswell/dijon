from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from dijon import crud, schemas
from dijon.dependencies import Context


router = APIRouter()


@router.get("/snapshots", response_model=list[schemas.Snapshot], status_code=HTTP_200_OK)
def list_snapshots(ctx: Context = Depends()):
    snapshots = []
    last = None  # use this to make sure we only return the latest snapshot for each server for each day
    for db_snapshot in crud.get_snapshots(ctx.db):
        snapshot = schemas.Snapshot(root_server_id=db_snapshot.root_server_id, date=db_snapshot.created_at.date())
        if last and snapshot.root_server_id == last.root_server_id and snapshot.date == last.date:
            snapshots.pop()
        snapshots.append(snapshot)
        last = snapshot
    return snapshots
