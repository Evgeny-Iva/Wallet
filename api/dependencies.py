from fastapi import Header, HTTPException, Depends
from jose import jwt
from api.config import settings
from api.blacklist import is_token_blacklisted
from api.model import User
from api.database import get_db, AsyncSession
from sqlalchemy import select


async def get_current_user(
        authorization: str = Header(...),
        db: AsyncSession = Depends(get_db)
) -> User:
    token = authorization.replace("Bearer ", "")

    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token revoked")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).filter_by(id=user_id)
    )
    user = result.scalar_one_or_none()

    return user