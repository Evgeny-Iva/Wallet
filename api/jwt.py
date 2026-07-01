from jose import jwt
from api.config import settings


def create_access_token(user_id: int) -> str:
    token = jwt.encode(
        {"sub": str(user_id)},
        settings.JWT_SECRET_KEY,
        "HS256"
    )
    return token