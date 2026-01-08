
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import UserCreate, RefreshTokenRequest, Token
from app.services.auth import AuthServiceDep

router = APIRouter()

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth: AuthServiceDep,
):
    return await auth.register(user_data)

@router.post(
    "/token",
    response_model=Token,
)
async def token(
    auth: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    return await auth.create_tokens_for_user(user)

@router.post(
    "/token/refresh",
    response_model=Token,
)
async def token_refresh(
    req: RefreshTokenRequest,
    auth: AuthServiceDep,
):
    user = await auth.refresh_tokens(req.refresh_token)
    return await auth.create_tokens_for_user(user)


# @router.post("/logout")
# async def logout(refresh_token: str, token_repo: TokenRepositoryDep):
#     await token_repo.revoke_refresh_token(refresh_token)
#     return {"msg": "Logged out"}
