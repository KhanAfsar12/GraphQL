# schemas.py - GraphQL schemas
import strawberry
from typing import List, Optional

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: str

@strawberry.type
class PostType:
    id: int
    title: str
    content: str
    created_at: str
    author: UserType

@strawberry.input
class UserInput:
    name: str
    email: str
    age: Optional[int] = None

@strawberry.input
class UserUpdateInput:
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None

@strawberry.input
class PostInput:
    title: str
    content: str
    author_id: int