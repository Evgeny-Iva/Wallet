from fastapi import Header, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from api.config import settings
from api.core.blacklist import is_token_blacklisted
from api.models.user import User
from api.database import get_db, AsyncSession
from sqlalchemy import select


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Получить текущего пользователя по JWT токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

    if user is None:
        raise credentials_exception

    return user