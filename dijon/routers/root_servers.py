from fastapi import APIRouter, Depends, HTTPException, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from dijon import crud, schemas
from dijon.dependencies import Context


router = APIRouter()


@router.get("/rootservers", response_model=list[schemas.RootServer], status_code=HTTP_200_OK)
def list_root_servers(ctx: Context = Depends()):
    return crud.get_root_servers(ctx.db)


@router.get("/rootservers/{root_server_id}", response_model=schemas.RootServer, status_code=HTTP_200_OK)
def get_root_server(root_server_id: int, ctx: Context = Depends()):
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

    return crud.create_root_server(ctx.db, root_server.name, root_server.url, root_server.is_enabled)


@router.patch("/rootservers/{root_server_id}", status_code=HTTP_204_NO_CONTENT, response_class=Response)
def update_root_server(root_server: schemas.RootServerUpdate, root_server_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.update_root_server(ctx.db, root_server_id, root_server.name, root_server.url, root_server.is_enabled):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.delete("/rootservers/{root_server_id}", status_code=HTTP_204_NO_CONTENT, response_class=Response)
def delete_root_server(root_server_id: int, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    if not crud.delete_root_server(ctx.db, root_server_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
