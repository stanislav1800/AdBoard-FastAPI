from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class MessageBase(BaseModel):
    text: str
    is_read: bool = False

class MessageCreateAPI(BaseModel):
    text: str

class MessageCreateInternal(BaseModel):
    chat_id: int
    sender_id: int
    text: str

class MessageDBCreate(MessageCreateInternal):
    is_read: bool = False

class MessageCreate(MessageBase):
    chat_id: SkipJsonSchema[int] = Field(default=None)
    sender_id: SkipJsonSchema[int] = Field(default=None)

class MessageDetail(MessageBase):
    id: int
    sender_id: int
    chat_id: int
    created_at: datetime
