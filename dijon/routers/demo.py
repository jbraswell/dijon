from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from dijon import crud, schemas
from dijon.dependencies import Context


router = APIRouter()


@router.get('/ping', status_code=HTTP_200_OK)
def ping():
    return 'pong'


@router.post('/echo', response_model=schemas.EchoResponse, status_code=HTTP_201_CREATED)
def echo(echo_request: schemas.EchoRequest, ctx: Context = Depends()):
    return crud.create_echo(ctx.db_session, echo_request.message)
