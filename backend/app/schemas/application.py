from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl


class ApplicationStatus(str, Enum):
    """Allowed status values; using an enum makes invalid values fail validation."""

    APPLIED = "Applied"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    OFFER = "Offer"
    WITHDRAWN = "Withdrawn"


class ApplicationBase(BaseModel):
    """Fields the user provides when creating or replacing an application."""

    company: str
    position: str
    status: ApplicationStatus
    application_date: date
    # Optional fields may be omitted or sent as null; HttpUrl rejects malformed URLs.
    job_url: HttpUrl | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    """POST body: the server assigns the ID, so clients do not provide it."""


class ApplicationUpdate(ApplicationBase):
    """PUT body: all editable fields are required for a full replacement."""


class Application(ApplicationBase):
    """Response schema, including the ID assigned by the server."""

    id: int

    # Allows Pydantic to validate an object stored as a Python dictionary.
    model_config = ConfigDict(from_attributes=True)
