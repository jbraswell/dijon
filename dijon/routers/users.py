from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from dijon import crud, schemas
from dijon.dependencies import Context


router = APIRouter()


@router.post(
    "/users",
    status_code=HTTP_201_CREATED,
    response_model=schemas.User,
)
def create_user(user: schemas.UserCreate, ctx: Context = Depends()):
    if not ctx.is_authenticated:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    db_user = crud.create_user(ctx.db, user.username, user.email, user.password, user.is_active, user.is_admin)
    if not db_user:
        raise HTTPException(status_code=HTTP_409_CONFLICT)

    return db_user
