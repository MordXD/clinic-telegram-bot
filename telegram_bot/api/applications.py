from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from telegram_bot.db.models import Application
from telegram_bot.db.session import get_session
from sqlmodel import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["applications"])

class ApplicationCreate(BaseModel):
    name: str
    phone: str
    comment: str = None

class ApplicationRead(BaseModel):
    id: int
    name: str
    phone: str
    comment: str = None
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(application: ApplicationCreate, session: Session = Depends(get_session)):
    db_application = Application(**application.dict())
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application

@router.get("/", response_model=List[ApplicationRead])
def read_applications(session: Session = Depends(get_session)):
    return session.exec(select(Application)).all()

@router.get("/{application_id}", response_model=ApplicationRead)
def read_application(application_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    session.delete(application)
    session.commit()
    return None 