
from .base import BaseRepository
from app.models.moderation import ModerationLog

class ModerationLogRepository(BaseRepository[ModerationLog]):
    pass
