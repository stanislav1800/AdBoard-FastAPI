from datetime import datetime
import re
from typing import Optional, Annotated

from pydantic import EmailStr, BaseModel, model_validator, constr

from app.models.user import UserRoleEnum, CityEnum


phone_regex = r'^((\+7)|8)\d{10}$'

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    location: Optional[CityEnum] = None
    bio: Optional[str] = None
    phone_number: Optional[Annotated[str, constr(pattern=phone_regex)]] = None

class UserAuthenticate(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password1: str
    password2: str

    @model_validator(mode="after")
    def password_strength(self):
        # if len(self.password1) < 8:
        #     raise ValueError('Password must be at least 8 characters long')
        # if not re.search(r'[A-Z]', self.password1):
        #     raise ValueError('Password must contain an uppercase letter')
        # if not re.search(r'[a-z]', self.password1):
        #     raise ValueError('Password must contain a lowercase letter')
        # if not re.search(r'[0-9]', self.password1):
        #     raise ValueError('Password must contain a digit')
        if self.password1 != self.password2:
            raise ValueError("Passwords do not match")
        return self

class UserPatch(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    location: Optional[CityEnum] = None
    bio: Optional[str] = None
    phone_number: Optional[Annotated[str, constr(pattern=phone_regex)]] = None

class UserPut(BaseModel):
    username: str
    email: EmailStr
    avatar: str
    location: CityEnum
    bio: str
    phone_number: Annotated[str, constr(pattern=phone_regex)]

class UserUpdateAdmin(UserPatch):
    role: Optional[UserRoleEnum] = None
    is_active: bool = None

class UserDetail(UserBase):
    id: int
    is_active: bool
    last_seen: Optional[datetime]

class UserDetailAdmin(UserDetail):
    role: UserRoleEnum
