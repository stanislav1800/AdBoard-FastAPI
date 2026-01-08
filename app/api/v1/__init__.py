from fastapi import APIRouter

from . import auth, users, listings, chats

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(chats.router, prefix="/chat", tags=["Chat"])
router.include_router(listings.router, prefix="/listing", tags=["Listing"])
router.include_router(users.router, prefix="/user", tags=["User"])
