from typing import Annotated

from fastapi import Depends
import jwt

from app.core.config import settings
from app.core.exceptions import IncorrectUsernameOrPasswordException, InvalidRefreshTokenException, PasswordsNotMatchException, RefreshTokenExpiredException, UserAlreadyExistsException, UserNotFoundException
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_token, decode_jwt_token
from app.models import User
from app.repositories import UserRepositoryDep, UserRepository
from app.schemas import Token, UserAuthenticate, UserCreate


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register(self, user_data: UserCreate) -> User:
        user = await self.user_repo.get_by_filters(username=user_data.username)
        if user:
            raise UserAlreadyExistsException
        
        if user_data.password1 != user_data.password2:
            raise PasswordsNotMatchException

        user = await self.user_repo.create(user_data)
        # return user
    
    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_repo.authenticate(UserAuthenticate(username=username, password=password))
        if not user:
            raise IncorrectUsernameOrPasswordException
        return user
    
    async def refresh_tokens(self, refresh_token: str) -> Token:
        """
        Бизнес‑логика обновления токенов.
        """
        try:
            payload = decode_jwt_token(refresh_token)
            user_id = payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpiredException
        except jwt.PyJWTError:
            raise InvalidRefreshTokenException

        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundException
        return user

    async def create_tokens_for_user(self, user: User):
        return Token(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
            token_type="bearer",
        )

    async def get_current_user(self, token: str):
        token_data = verify_token(token)
        user = await self.user_repo.get_by_id(int(token_data.user_id))
        if not user:
            raise UserNotFoundException
        return user

    async def get_user_from_token(self, token: str):
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await self.user_repo.get_by_id(int(user_id))

def get_auth_service(
    user_repo: UserRepositoryDep,
) -> AuthService:
    return AuthService(user_repo)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
