from datetime import datetime

from pydantic import BaseModel


class ListingFavoriteBase(BaseModel):
    listing_id: int
    user_id: int

class ListingFavoriteDetail(ListingFavoriteBase):
    id: int
    created_at: datetime