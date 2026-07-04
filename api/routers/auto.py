from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy import select
from api.database import get_db, AsyncSession
from api.dependencies.dependencies import get_current_user
from pydantic import BaseModel
from api.core.hashing import hash_password, verify_password
from api.core.jwt import create_access_token
from api.core.blacklist import add_to_blacklist
from api.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).filter_by(email=user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user_data.password)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hashed
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"massage": "User created", "user_id": new_user.id}


@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).filter_by(email=user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    is_password_valid = verify_password(user_data.password, existing_user.password_hash)

    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"access_token": create_access_token(existing_user.id), "token_type": "bearer"}


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user),
        authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")
    add_to_blacklist(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Logged out"}