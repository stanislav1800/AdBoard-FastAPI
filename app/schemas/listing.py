from typing import Optional

from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

from app.schemas.listing_image import ListingImageDetail

from .category import CategoryDetail
from app.models.listing import ConditionEnum, StatusEnum


class ListingBase(BaseModel):
    title: str
    description: str | None = None
    price: float
    condition: ConditionEnum
    location: str
    status: StatusEnum = StatusEnum.MODERATION

class ListingCreate(ListingBase):
    category_ids: Optional[list[int]] = []
    # user_id: SkipJsonSchema[int]

class ListingUpdate(BaseModel):
    id: SkipJsonSchema[int]

class ListingPut(BaseModel):
    # user_id: SkipJsonSchema[int]
    title: str
    description: str | None
    price: float
    condition: ConditionEnum
    location: str
    status: StatusEnum
    categories: list[int] = []

class ListingPatch(BaseModel):
    # user_id: SkipJsonSchema[int]
    title: str | None = None
    description: str | None = None
    price: float | None = None
    condition: ConditionEnum | None = None
    location: str | None = None
    status: StatusEnum | None = None
    categories: Optional[list[int]] = None

class ListingDetail(ListingBase):
    id: int
    user_id: int
    categories: list[CategoryDetail] = []
    listing_images: list[ListingImageDetail] = []
    views_count: int
    
