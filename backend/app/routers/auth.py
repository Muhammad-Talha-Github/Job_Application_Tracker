from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserLogin, UserRegister, UserResponse
from app.services.passwords import hash_password, verify_password
from app.services.tokens import create_access_token


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)) -> User:
    """Validate and hash a new password before storing a user account."""
    email = str(user_data.email).lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(email=email, password_hash=hash_password(user_data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # The unique constraint also handles two simultaneous registrations safely.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Check the stored Argon2 hash and return a short-lived JWT on success."""
    email = str(credentials.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(credentials.password, user.password_hash):
        # Use the same response for unknown email and wrong password.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))
