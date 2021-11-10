from pydantic import BaseModel


class Echo(BaseModel):
    message: str


class EchoRequest(Echo):
    pass


class EchoResponse(Echo):
    id: int

    class Config:
        orm_mode = True
