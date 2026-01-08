
from sqlalchemy.exc import IntegrityError

from .base import BaseRepository
from app.core.exceptions import FailedCreateMessageException
from app.models.message import Message

class MessageRepository(BaseRepository[Message]):
    
    async def create(self, *args, **kwargs) -> Message:
        try:
            return await super().create(*args, **kwargs)
        except IntegrityError as e:
            raise FailedCreateMessageException
