from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    slug: str
    order: int

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryDetail(CategoryBase):
    id: int
