import os

from dotenv import load_dotenv


# Values are loaded from backend/.env locally or from the process environment elsewhere.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Set it in backend/.env.")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be set to a random value of at least 32 characters.")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
if ACCESS_TOKEN_MINUTES < 1:
    raise RuntimeError("ACCESS_TOKEN_MINUTES must be a positive integer.")

# Comma-separated exact browser origins; never use '*' for this authenticated API.
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
if "*" in FRONTEND_ORIGINS:
    raise RuntimeError("FRONTEND_ORIGINS must list explicit origins; '*' is not allowed.")
