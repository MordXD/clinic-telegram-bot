from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = None
    username: Optional[str] = None
    rating: int
    dislikes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow) 