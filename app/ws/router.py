
from fastapi import APIRouter, Query, WebSocket, WebSocketException, status

from app.core.database import SessionFactoryDep
from .handler import ChatSocketHandler, authenticate_ws
from .runtime import WSRuntimeDep

router = APIRouter()

@router.websocket("")
async def ws_endpoint(
    websocket: WebSocket,
    runtime: WSRuntimeDep,
    session_factory: SessionFactoryDep,
    token: str | None = Query(None),
):
    user = await authenticate_ws(session_factory, token)
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await ChatSocketHandler(websocket, user, runtime, session_factory).run()

@router.get("/docs", tags=["WebSocket"])
def ws_docs():
    """
    ## WebSocket API

    Одно соединение на клиента: `ws://localhost:8000/ws?token=<access_token>`.
    Невалидный токен — соединение отклоняется с кодом 1008.

    ### Клиент → сервер
    - `{"action": "subscribe", "chat_id": 5}` — подписка на события чата (проверяется участие)
    - `{"action": "unsubscribe", "chat_id": 5}`
    - `{"action": "typing", "chat_id": 5}` — «печатает…» (только для подписанного чата)
    - `{"action": "ping"}` → `{"type": "pong"}`

    ### Сервер → клиент
    Приходят всегда (подписка на пользователя автоматическая):
    - `{"type": "chat_list_update", "chat_id", "last_message"}`
    - `{"type": "unread_count", "chat_id"}`

    По подписанным чатам:
    - `{"type": "new_message", "chat_id", "sender_id", "text"}`
    - `{"type": "typing", "chat_id", "user_id"}`

    Служебные: `subscribed`, `unsubscribed`, `error` (`action`, `chat_id`, `detail`).
    """
    return {"detail": "WebSocket endpoints"}
