from datetime import datetime

from pydantic import BaseModel


class Fund(BaseModel):
    id: str
    name: str


class Quote(BaseModel):
    Date: datetime
    Close: float


class Message(BaseModel):
    message: str
