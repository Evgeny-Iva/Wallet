from api.core.redis_client import redis_client


def add_to_blacklist(token: str, expires: int) -> None:
    redis_client.setex(
        f"blacklist:{token}",
        expires,
        "revoked"
    )


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}") == 1
