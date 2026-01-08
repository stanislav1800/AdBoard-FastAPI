from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.models.moderation import ActionEnum

class ModerationLogBase(BaseModel):
    action: ActionEnum
    reason: str

class ModerationLogCreate(ModerationLogBase):
    listing_id: int | None = None
    moderator_id: int | None = None

class ModerationLogDetail(ModerationLogBase):
    id: int
    listing_id: int
    moderator_id: int
    create_at: datetime
