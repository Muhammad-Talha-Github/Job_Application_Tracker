from datetime import datetime, timedelta, timezone

import jwt

from app.config import ACCESS_TOKEN_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY


def create_access_token(user_id: int) -> str:
    """Sign a short-lived token containing only the user ID and token times."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
