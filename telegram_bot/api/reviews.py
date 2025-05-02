from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from telegram_bot.db.models import Review
from telegram_bot.db.session import get_session
from sqlmodel import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/reviews", tags=["reviews"])

class ReviewCreate(BaseModel):
    user_id: int = None
    username: str = None
    rating: int
    dislikes: str = None

class ReviewRead(BaseModel):
    id: int
    user_id: int = None
    username: str = None
    rating: int
    dislikes: str = None
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    db_review = Review(**review.dict())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review

@router.get("/", response_model=List[ReviewRead])
def read_reviews(session: Session = Depends(get_session)):
    return session.exec(select(Review)).all()

@router.get("/{review_id}", response_model=ReviewRead)
def read_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    session.delete(review)
    session.commit()
    return None 