from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class UserRatingBase(BaseModel):
    score: float
    comment: str

class UserRatingPost(UserRatingBase):
    pass

class UserRatingCreate(UserRatingBase):
    user_id: SkipJsonSchema[int] = None
    rater_id: SkipJsonSchema[int] = Field(default=None)

class UserRatingDetail(UserRatingBase):
    id: int
    user_id: int
    rater_id: int
    created_at: datetime
