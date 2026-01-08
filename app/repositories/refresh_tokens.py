from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from .base import BaseRepository
from app.core.database import SessionDep
from app.models.refresh_tokens import RefreshToken

class TokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    async def add_refresh_token(self, user_id: int, token: str):
        rt = RefreshToken(user_id=user_id, token=token)
        self.db.add(rt)
        await self.db.commit()
        return rt

    async def revoke_refresh_token(self, token: str):
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        rt = result.scalar_one_or_none()
        if rt:
            rt.revoked = True
            await self.db.commit()

    async def is_refresh_token_valid(self, token: str) -> bool:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        rt = result.scalar_one_or_none()
        return bool(rt and not rt.revoked)

async def get_user_repository(db: SessionDep) -> TokenRepository:
    return TokenRepository(db)

TokenRepositoryDep = Annotated[TokenRepository, Depends(get_user_repository)]
