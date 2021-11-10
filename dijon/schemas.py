from pydantic import BaseModel


class Echo(BaseModel):
    message: str


class EchoRequest(Echo):
    pass


class EchoResponse(Echo):
    class Config:
        orm_mode = True
