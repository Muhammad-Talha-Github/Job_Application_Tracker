from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


# Keep a passphrase-friendly minimum while bounding input size for hashing.
PasswordInput = Annotated[str, StringConstraints(min_length=12, max_length=128)]
PasswordForLogin = Annotated[str, StringConstraints(min_length=1, max_length=128)]


class UserRegister(BaseModel):
    email: EmailStr
    password: PasswordInput


class UserLogin(BaseModel):
    email: EmailStr
    password: PasswordForLogin


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    # This response intentionally has no password or password_hash field.
    model_config = ConfigDict(from_attributes=True)
