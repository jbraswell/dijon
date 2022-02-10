from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from dijon import crud, schemas, snapshot
from dijon.dependencies import Context
from dijon.snapshot import structs


router = APIRouter()


@router.get("/rootservers", response_model=list[schemas.RootServer], status_code=HTTP_200_OK)
def list_root_servers(ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    return crud.get_root_servers(ctx.db)


@router.get("/rootservers/{root_server_id}", response_model=schemas.RootServer, status_code=HTTP_200_OK)
def get_root_server(root_server_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_root_server = crud.get_root_server(ctx.db, root_server_id)
    if not db_root_server:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return db_root_server


@router.post("/rootservers", response_model=schemas.RootServer, status_code=HTTP_201_CREATED)
def create_root_server(root_server: schemas.RootServerCreate, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    root_server.url = root_server.url.strip()

    if not root_server.url.endswith("/"):
        root_server.url += "/"
    return crud.create_root_server(ctx.db, root_server.name, root_server.url)


@router.delete("/rootservers/{root_server_id}", status_code=HTTP_204_NO_CONTENT, response_class=Response)
def delete_root_server(root_server_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_root_server(ctx.db, root_server_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.get("/rootservers/{root_server_id}/snapshots/{date}/meetings", response_model=list[structs.Meeting], status_code=HTTP_200_OK)
def list_meetings(
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


@router.get("/rootservers/{root_server_id}/meetings/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_meeting_naws_codes(root_server_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    return crud.get_meeting_naws_codes_by_server(ctx.db, root_server_id)


@router.get("/rootservers/{root_server_id}/formats/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_format_naws_codes(root_server_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    return crud.get_format_naws_codes_by_server(ctx.db, root_server_id)


@router.get("/rootservers/{root_server_id}/servicebodies/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_service_body_naws_codes(root_server_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    return crud.get_service_body_naws_codes_by_server(ctx.db, root_server_id)


@router.get("/rootservers/{root_server_id}/meetings/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_meeting_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    naws_code = crud.get_meeting_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.get("/rootservers/{root_server_id}/formats/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_format_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    naws_code = crud.get_format_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.get("/rootservers/{root_server_id}/servicebodies/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_service_body_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    naws_code = crud.get_service_body_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.post("/rootservers/{root_server_id}/meetings/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_meeting_naws_code(root_server_id: int, naws_code: schemas.NawsCode, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_meeting_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.post("/rootservers/{root_server_id}/formats/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_format_naws_code(root_server_id: int, naws_code: schemas.NawsCode, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_format_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.post("/rootservers/{root_server_id}/servicebodies/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_service_body_naws_code(root_server_id: int, naws_code: schemas.NawsCode, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_service_body_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.delete("/rootservers/{root_server_id}/meetings/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_meeting_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_meeting_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.delete("/rootservers/{root_server_id}/formats/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_format_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_format_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.delete("/rootservers/{root_server_id}/servicebodies/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_service_body_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    # TODO write tests
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_service_body_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
