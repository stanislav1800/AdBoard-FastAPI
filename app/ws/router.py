
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.repositories import UserRepositoryDep
from app.api.deps import get_current_user_ws
from .manager import manager

router = APIRouter()

@router.websocket("/chat/{chat_id}")
async def ws_chat(websocket: WebSocket, chat_id: int, db: UserRepositoryDep, token: str = Query(None)):
    user = await get_current_user_ws(websocket, db, token)
    if chat_id not in user.chats:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    topic = f"chat:{chat_id}"
    manager.connect(websocket, topic)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)

@router.websocket("/typing/{chat_id}")
async def ws_typing(ws: WebSocket, chat_id: int, db: UserRepositoryDep):
    user = await get_current_user_ws(ws, db)
    if chat_id not in user.chats:
        await ws.close(code=1008)
        return
    await ws.accept()
    topic = f"typing:{chat_id}"
    manager.connect(ws, topic)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, topic)

@router.websocket("/chat-list")
async def ws_chat_list(ws: WebSocket, db: UserRepositoryDep):
    user = await get_current_user_ws(ws, db)
    await ws.accept()
    topic = f"chat_list:{user.id}"
    manager.connect(ws, topic)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, topic)

@router.websocket("/unread")
async def ws_unread(ws: WebSocket, db: UserRepositoryDep):
    user = await get_current_user_ws(ws, db)
    await ws.accept()
    topic = f"unread:{user.id}"
    await manager.connect(ws, topic)

    try:
        while True:
            data = await ws.receive_text()
            await manager.publish(topic, data)
    except WebSocketDisconnect:
        manager.disconnect(ws, topic)

@router.get("/ws", tags=["WebSocket"])
def ws_docs():
    """
    ## WebSocket API

    ### 1. Чат конкретного диалога
    `ws://localhost:8000/ws/chat/{chat_id}`
    - Топик: chat:{chat_id}
    - Auth: проверка участия в чате

    ### 2. Список чатов пользователя
    `ws://localhost:8000/ws/chat-list`
    - Топик: chat_list:{user.id}
    - Auth: JWT в cookie/headers

    ### 3. Счётчик непрочитанных сообщений
    `ws://localhost:8000/ws/unread`
    - Топик: unread:{user.id}
    - Auth: JWT

    ### 4. Набор текста (typing)
    `ws://localhost:8000/ws/typing/{chat_id}`
    - Топик: typing:{chat_id}
    - Auth: JWT
    """
    return {"detail": "WebSocket endpoints"}
