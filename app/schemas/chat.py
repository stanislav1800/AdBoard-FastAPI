from pydantic import BaseModel

from .message import MessageDetail
from .user import UserDetail
from .listing import ListingDetail


class ChatBase(BaseModel):
    listing_id: int

class ChatCreate(ChatBase):
    participant_ids: list[int]

class ChatDetail(ChatBase):
    id: int
    participants: list[UserDetail] = []
    messages: list[MessageDetail] = []
    listing: ListingDetail
