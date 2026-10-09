import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import FRONTEND_ORIGINS
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

# Allow only configured local or deployed frontend origins, never every website.
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Keeping routes in a router makes the endpoint code easier to find as the API grows.
app.include_router(applications_router)
app.include_router(auth_router)
