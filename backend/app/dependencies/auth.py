import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import get_db
from app.models.user import User


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate a bearer JWT and load its user for a protected endpoint."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, TypeError, ValueError, KeyError):
        raise unauthorized from None

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user
