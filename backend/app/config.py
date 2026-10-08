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
