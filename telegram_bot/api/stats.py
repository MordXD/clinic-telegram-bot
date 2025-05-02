from fastapi import APIRouter, Depends
from telegram_bot.db.session import get_session
from sqlmodel import Session, select
from telegram_bot.db.models import Application, Review

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats(session: Session = Depends(get_session)):
    applications_count = session.exec(select(Application)).count()
    reviews_count = session.exec(select(Review)).count()
    return {
        "applications_count": applications_count,
        "reviews_count": reviews_count
    } 