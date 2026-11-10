
from sqlalchemy import select, func, case, exists
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.sql import and_

from .base import BaseRepository
from app.models import Listing, User, Chat, Message, chat_participants

class ChatRepository(BaseRepository[Chat]):
    def _base_query(self):
        return (
            select(Chat)
            .options(
                selectinload(Chat.participants),
                selectinload(Chat.messages),
                selectinload(Chat.listing).selectinload(Listing.listing_images)
            )
        )
    
    async def get_chat_participants(self, chat_id: int) -> list[User]:
        stmt = (
            select(User)
            .join(chat_participants)
            .where(chat_participants.c.chat_id == chat_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def user_can_write(self, chat_id: int, user_id: int) -> bool:
        stmt = select(
            exists().where(
                Chat.id == chat_id,
                Chat.participants.any(User.id == user_id)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar()
    
    async def get_detail(self, chat_id: int) -> Chat | None:
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(
                selectinload(Chat.participants),
                selectinload(Chat.messages),
                selectinload(Chat.listing).selectinload(Listing.listing_images)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_chats(self, user_id: int):
        stmt = (
            select(self.model)
            .where(self.model.participants.any(User.id == user_id))
            .options(
                selectinload(self.model.messages),
                selectinload(self.model.participants),
                selectinload(self.model.listing).selectinload(Listing.listing_images),
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def chat_lazy_create(self, user_id, seller_id, listing_id):
        stmt = (
            select(Chat)
            .where(
                Chat.participants.any(User.id == user_id),
                Chat.participants.any(User.id == seller_id),
                Chat.listing_id == listing_id
            )
        )
        result = await self.db.execute(stmt)
        chat = result.scalar_one_or_none()
        
        if not chat:
            chat = Chat(listing_id=listing_id)
            
            user = await self.db.get(User, user_id)
            seller = await self.db.get(User, seller_id)
            
            chat.participants.extend([user, seller])
            
            self.db.add(chat)
            await self.db.commit()
            await self.db.refresh(chat)
        
        return chat
    
    async def get_unread(self, request_user_id: int):
        MessageAlias = aliased(Message)
        ParticipantAlias = aliased(User)

        unread_chats = (
            select(Chat.id)
            .join(Chat.participants.of_type(ParticipantAlias))
            .outerjoin(MessageAlias, MessageAlias.chat_id == Chat.id)
            .where(ParticipantAlias.id == request_user_id)
            .group_by(Chat.id)
            .having(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                and_(
                                    MessageAlias.is_read == False,
                                    MessageAlias.sender_id != request_user_id
                                ),
                                1
                            ),
                            else_=0
                        )
                    ),
                    0
                ) > 0
            )
            .subquery()
        )
        stmt = select(func.count()).select_from(unread_chats)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

