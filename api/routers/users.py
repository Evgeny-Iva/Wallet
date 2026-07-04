from fastapi import APIRouter, Depends
from api.models.user import User
from api.dependencies.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "middle_name": current_user.middle_name,
        "created_at": current_user.created_at
    }