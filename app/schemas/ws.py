from typing import Literal

from pydantic import BaseModel


class WSClientMessage(BaseModel):
    """Сообщение клиента в /ws"""
    action: Literal["subscribe", "unsubscribe", "typing", "ping"]
    chat_id: int | None = None
