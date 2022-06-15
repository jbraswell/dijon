from datetime import date
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, EmailStr, constr

from dijon.snapshot.diff import structs


# Root Server
#
#
class RootServerBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    url: AnyHttpUrl

    class Config:
        orm_mode = True


class RootServer(RootServerBase):
    id: int


class RootServerCreate(RootServerBase):
    pass


class RootServerUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)]
    url: Optional[AnyHttpUrl]


# User
#
#
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool


class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]
    is_admin: Optional[bool]


class UserCreate(UserBase):
    password: str
    is_active: bool
    is_admin: Optional[bool] = False

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


# Token
#
#
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class Logout(BaseModel):
    refresh_token: str


# MeetingChanges
#
#
class MeetingChangesResponse(BaseModel):
    start_date: date
    end_date: date
    events: list[structs.MeetingEvent]


# NawsCodes
#
#
class NawsCodeCreate(BaseModel):
    bmlt_id: int
    code: str

    class Config:
        orm_mode = True


class NawsCode(NawsCodeCreate):
    root_server_id: int

    class Config:
        orm_mode = True


# Snapshots
#
#
class Snapshot(BaseModel):
    root_server_id: int
    date: date

    class Config:
        orm_mode = True
