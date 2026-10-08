import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.routers.auth import router as auth_router
from app.routers.applications import router as applications_router


# The FastAPI object is the application server entry point used by Uvicorn.
app = FastAPI(title="Job Application Tracker API")


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_request, _exception: SQLAlchemyError) -> JSONResponse:
    """Keep database details in server logs and return a clear API error to clients."""
    logging.exception("Database request failed")
    return JSONResponse(
        status_code=503,
        content={"detail": "Database operation failed. Please try again later."},
    )

# Browsers enforce CORS when the Vite page (port 5173) calls this API (port 8000).
# Allow only the local development origins used by Vite, with the CRUD methods needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Keeping routes in a router makes the endpoint code easier to find as the API grows.
app.include_router(applications_router)
app.include_router(auth_router)
