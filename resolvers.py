# resolvers.py - GraphQL resolvers
from sqlmodel import Session, select
from database import engine
from models import User, Post
from schemas import UserType, PostType, UserInput, UserUpdateInput, PostInput
import strawberry
from typing import List, Optional

class UserResolver:
    
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL with FastAPI!"
    
    @strawberry.field
    def users(self, limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[UserType]:
        with Session(engine) as session:
            statement = select(User).offset(offset).limit(limit)
            users = session.exec(statement).all()
            
            return [
                UserType(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    age=user.age,
                    created_at=user.created_at.isoformat()
                )
                for user in users
            ]
    
    @strawberry.field
    def user(self, id: int) -> Optional[UserType]:
        with Session(engine) as session:
            user = session.get(User, id)
            if user:
                return UserType(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    age=user.age,
                    created_at=user.created_at.isoformat()
                )
            return None

class UserMutation:
    
    @strawberry.mutation
    def create_user(self, user_input: UserInput) -> UserType:
        with Session(engine) as session:
            # Check if user already exists
            existing_user = session.exec(select(User).where(User.email == user_input.email)).first()
            if existing_user:
                raise Exception("User with this email already exists")
            
            user = User(
                name=user_input.name,
                email=user_input.email,
                age=user_input.age
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            return UserType(
                id=user.id,
                name=user.name,
                email=user.email,
                age=user.age,
                created_at=user.created_at.isoformat()
            )
    
    @strawberry.mutation
    def update_user(self, id: int, user_input: UserUpdateInput) -> Optional[UserType]:
        with Session(engine) as session:
            user = session.get(User, id)
            if not user:
                raise Exception("User not found")
            
            if user_input.name is not None:
                user.name = user_input.name
            if user_input.email is not None:
                user.email = user_input.email
            if user_input.age is not None:
                user.age = user_input.age
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            return UserType(
                id=user.id,
                name=user.name,
                email=user.email,
                age=user.age,
                created_at=user.created_at.isoformat()
            )
    
    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        with Session(engine) as session:
            user = session.get(User, id)
            if not user:
                raise Exception("User not found")
            
            session.delete(user)
            session.commit()
            return True

class PostResolver:
    
    @strawberry.field
    def posts(self, limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[PostType]:
        with Session(engine) as session:
            statement = select(Post).offset(offset).limit(limit)
            posts = session.exec(statement).all()
            
            result = []
            for post in posts:
                result.append(
                    PostType(
                        id=post.id,
                        title=post.title,
                        content=post.content,
                        created_at=post.created_at.isoformat(),
                        author=UserType(
                            id=post.author.id,
                            name=post.author.name,
                            email=post.author.email,
                            age=post.author.age,
                            created_at=post.author.created_at.isoformat()
                        )
                    )
                )
            return result

class PostMutation:
    
    @strawberry.mutation
    def create_post(self, post_input: PostInput) -> PostType:
        with Session(engine) as session:
            # Check if author exists
            author = session.get(User, post_input.author_id)
            if not author:
                raise Exception("Author not found")
            
            post = Post(
                title=post_input.title,
                content=post_input.content,
                author_id=post_input.author_id
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            
            # Refresh to get author data
            post_with_author = session.get(Post, post.id)
            
            return PostType(
                id=post_with_author.id,
                title=post_with_author.title,
                content=post_with_author.content,
                created_at=post_with_author.created_at.isoformat(),
                author=UserType(
                    id=post_with_author.author.id,
                    name=post_with_author.author.name,
                    email=post_with_author.author.email,
                    age=post_with_author.author.age,
                    created_at=post_with_author.author.created_at.isoformat()
                )
            )