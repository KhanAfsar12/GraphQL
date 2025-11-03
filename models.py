# models.py - Database models
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    posts: List["Post"] = Relationship(back_populates="author")

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    author: User = Relationship(back_populates="posts")