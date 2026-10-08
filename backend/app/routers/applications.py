from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.application import Application as ApplicationModel
from app.models.user import User
from app.schemas.application import Application, ApplicationCreate, ApplicationUpdate


router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[Application])
def list_applications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ApplicationModel]:
    """Return only rows owned by the authenticated user."""
    query = select(ApplicationModel).where(ApplicationModel.user_id == current_user.id)
    return list(db.scalars(query.order_by(ApplicationModel.id)).all())


@router.get("/{application_id}", response_model=Application)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationModel:
    """Read one owned row; a row belonging to someone else is also hidden as 404."""
    query = select(ApplicationModel).where(
        ApplicationModel.id == application_id,
        ApplicationModel.user_id == current_user.id,
    )
    application = db.scalar(query)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.post("", response_model=Application, status_code=status.HTTP_201_CREATED)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationModel:
    """Insert a row for the authenticated user; the client cannot choose its owner."""
    values = application_data.model_dump()
    if values["job_url"] is not None:
        values["job_url"] = str(values["job_url"])
    application = ApplicationModel(**values, user_id=current_user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.put("/{application_id}", response_model=Application)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationModel:
    """Replace fields only when the row belongs to the authenticated user."""
    query = select(ApplicationModel).where(
        ApplicationModel.id == application_id,
        ApplicationModel.user_id == current_user.id,
    )
    application = db.scalar(query)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    values = application_data.model_dump()
    if values["job_url"] is not None:
        values["job_url"] = str(values["job_url"])
    for field, value in values.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete only an owned row and preserve the existing empty 204 response."""
    query = select(ApplicationModel).where(
        ApplicationModel.id == application_id,
        ApplicationModel.user_id == current_user.id,
    )
    application = db.scalar(query)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    db.delete(application)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
