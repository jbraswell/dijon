from fastapi import APIRouter, Depends, HTTPException, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from dijon import crud, schemas
from dijon.dependencies import Context


router = APIRouter()


@router.get("/meetings/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_meeting_naws_codes(ctx: Context = Depends()):
    return crud.get_meeting_naws_codes(ctx.db)


@router.get("/formats/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_format_naws_codes(ctx: Context = Depends()):
    return crud.get_format_naws_codes(ctx.db)


@router.get("/servicebodies/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_service_body_naws_codes(ctx: Context = Depends()):
    return crud.get_service_body_naws_codes(ctx.db)


@router.get("/rootservers/{root_server_id}/meetings/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_server_meeting_naws_codes(root_server_id: int, ctx: Context = Depends()):
    return crud.get_meeting_naws_codes(ctx.db, root_server_id=root_server_id)


@router.get("/rootservers/{root_server_id}/formats/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_server_format_naws_codes(root_server_id: int, ctx: Context = Depends()):
    return crud.get_format_naws_codes(ctx.db, root_server_id=root_server_id)


@router.get("/rootservers/{root_server_id}/servicebodies/nawscodes", response_model=list[schemas.NawsCode], status_code=HTTP_200_OK)
def list_server_service_body_naws_codes(root_server_id: int, ctx: Context = Depends()):
    return crud.get_service_body_naws_codes(ctx.db, root_server_id=root_server_id)


@router.get("/rootservers/{root_server_id}/meetings/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_meeting_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    naws_code = crud.get_meeting_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.get("/rootservers/{root_server_id}/formats/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_format_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    naws_code = crud.get_format_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.get("/rootservers/{root_server_id}/servicebodies/nawscodes/{bmlt_id}", response_model=schemas.NawsCode, status_code=HTTP_200_OK)
def get_service_body_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    naws_code = crud.get_service_body_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id)
    if not naws_code:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return naws_code


@router.post("/rootservers/{root_server_id}/meetings/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_meeting_naws_code(root_server_id: int, naws_code: schemas.NawsCodeCreate, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_meeting_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.post("/rootservers/{root_server_id}/formats/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_format_naws_code(root_server_id: int, naws_code: schemas.NawsCodeCreate, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_format_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.post("/rootservers/{root_server_id}/servicebodies/nawscodes", response_model=schemas.NawsCode, status_code=HTTP_201_CREATED)
def create_service_body_naws_code(root_server_id: int, naws_code: schemas.NawsCodeCreate, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_naws_code = crud.create_service_body_naws_code(ctx.db, root_server_id, naws_code.bmlt_id, naws_code.code)
    if not db_naws_code:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    return db_naws_code


@router.patch("/rootservers/{root_server_id}/meetings/nawscodes", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def batch_update_meeting_naws_codes(root_server_id: int, naws_codes: list[schemas.NawsCodeCreate], ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    naws_codes_by_bmlt_id = {nc.bmlt_id: nc for nc in naws_codes}
    db_naws_codes = crud.get_meeting_naws_codes_by_bmlt_ids(ctx.db, root_server_id, list(naws_codes_by_bmlt_id.keys()), with_for_update=True)

    seen_bmlt_ids: set[str] = set()
    ids_to_delete: list[int] = []
    for db_naws_code in db_naws_codes:
        seen_bmlt_ids.add(db_naws_code.bmlt_id)
        new_naws_code = naws_codes_by_bmlt_id[db_naws_code.bmlt_id]
        if db_naws_code.code != new_naws_code.code:
            if new_naws_code.code.strip():
                crud.update_meeting_naws_code(ctx.db, root_server_id, new_naws_code.bmlt_id, new_naws_code.code)
            else:
                ids_to_delete.append(db_naws_code.id)

    if ids_to_delete:
        crud.delete_meeting_naws_codes(ctx.db, ids_to_delete)

    for new_naws_code in naws_codes_by_bmlt_id.values():
        if new_naws_code.bmlt_id not in seen_bmlt_ids:
            crud.create_meeting_naws_code(ctx.db, root_server_id, new_naws_code.bmlt_id, new_naws_code.code)


@router.delete("/rootservers/{root_server_id}/meetings/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_meeting_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_meeting_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.delete("/rootservers/{root_server_id}/formats/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_format_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_format_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.delete("/rootservers/{root_server_id}/servicebodies/nawscodes/{bmlt_id}", response_class=Response, status_code=HTTP_204_NO_CONTENT)
def delete_service_body_naws_code(root_server_id: int, bmlt_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_service_body_naws_code_by_bmlt_id(ctx.db, root_server_id, bmlt_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
