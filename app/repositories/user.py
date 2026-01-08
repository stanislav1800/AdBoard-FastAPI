
from sqlalchemy import select

from .base import BaseRepository
from app.models import User
from app.schemas import UserCreate, UserAuthenticate
from app.core.security import get_password_hash, verify_password

class UserRepository(BaseRepository[User]):
    async def create(self, obj_in: UserCreate) -> User:        
        obj = self.model(
            username=obj_in.username,
            password=get_password_hash(obj_in.password1),
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def authenticate(self, obj_in: UserAuthenticate) -> User:
        query = select(self.model).where(self.model.username == obj_in.username) 
        result = await self.db.execute(query) 
        user = result.scalar_one_or_none() 
        if user and verify_password(obj_in.password, user.password):
            return user
        return None
