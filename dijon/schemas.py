from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, EmailStr, constr


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
