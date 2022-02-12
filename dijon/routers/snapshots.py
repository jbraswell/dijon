from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

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


@router.get("/rootservers/{root_server_id}/snapshots", response_model=list[schemas.Snapshot], status_code=HTTP_200_OK)
def list_server_snapshots(root_server_id: int, ctx: Context = Depends()):
    snapshots = []
    last = None  # use this to make sure we only return the latest snapshot for each day
    for db_snapshot in crud.get_snapshots(ctx.db, root_server_id):
        snapshot = schemas.Snapshot(root_server_id=db_snapshot.root_server_id, date=db_snapshot.created_at.date())
        if last and snapshot.date == last.date:
            snapshots.pop()
        snapshots.append(snapshot)
        last = snapshot
    return snapshots


@router.get("/rootservers/{root_server_id}/snapshots/{date}", response_model=schemas.Snapshot, status_code=HTTP_200_OK)
def get_server_snapshot(root_server_id: int, date: date, ctx: Context = Depends()):
    db_snapshot = crud.get_snapshot_by_date(ctx.db, root_server_id, date)
    if not db_snapshot:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return schemas.Snapshot(root_server_id=db_snapshot.root_server_id, date=db_snapshot.created_at.date())
