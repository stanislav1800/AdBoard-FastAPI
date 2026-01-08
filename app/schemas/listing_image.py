from datetime import datetime

from pydantic import BaseModel


class ListingImageBase(BaseModel):
    image: str
    order: int
    is_primary: bool = False

class ListingImageDetail(BaseModel):
    id: int
    image: str
    order: int
    is_primary: bool
