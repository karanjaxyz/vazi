from fastapi import APIRouter, Depends

from models import User
from schemas.auth import UserResponse
from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return user
