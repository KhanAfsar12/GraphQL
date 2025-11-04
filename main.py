# main.py - FastAPI application
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter
from database import create_db_and_tables
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager


# Define types directly in main.py to avoid import issues
@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    age: Optional[int] = None
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
class PostInput:
    title: str
    content: str
    author_id: int

# Query class with all fields defined directly
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL with FastAPI!"
    
    @strawberry.field
    def users(self, limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[UserType]:
        from database import engine
        from sqlmodel import Session, select
        from models import User
        
        with Session(engine) as session:
            statement = select(User).offset(offset).limit(limit)
            users = session.exec(statement).all()
            print("statement->", statement)
            print("users->", users)
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
        from database import engine
        from sqlmodel import Session, select
        from models import User
        
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
    
    @strawberry.field
    def posts(self, limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[PostType]:
        from database import engine
        from sqlmodel import Session, select
        from models import Post, User
        
        with Session(engine) as session:
            statement = select(Post).offset(offset).limit(limit)
            posts = session.exec(statement).all()
            
            result = []
            for post in posts:
                # Ensure we have the author relationship loaded
                post_with_author = session.get(Post, post.id)
                result.append(
                    PostType(
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
                )
            return result
        
    @strawberry.field
    def post(self, id: int) -> Optional[PostType]:
        from database import engine
        from sqlmodel import Session, select
        from models import Post
        
        with Session(engine) as session:
            post = session.get(Post, id)
            if not post:
                return None

            post_with_author = session.get(Post, post.id)
            return PostType(
                id=post_with_author.id,
                title=post_with_author.title,
                content=post_with_author.content,
                created_at=post_with_author.created_at.isoformat(),
                author= UserType(
                    id=post_with_author.author.id,
                    name=post_with_author.author.name,
                    email=post_with_author.author.email,
                    age=post_with_author.author.age,
                    created_at=post_with_author.author.created_at.isoformat()
                )
            )


# Mutation class with all fields defined directly
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, user_input: UserInput) -> UserType:
        from database import engine
        from sqlmodel import Session, select
        from models import User
        
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
    def update_user(self, id: int, name: Optional[str] = None, email: Optional[str] = None, age: Optional[int] = None) -> Optional[UserType]:
        from database import engine
        from sqlmodel import Session, select
        from models import User
        
        with Session(engine) as session:
            user = session.get(User, id)
            if not user:
                raise Exception("User not found")
            
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if age is not None:
                user.age = age
            
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
        from database import engine
        from sqlmodel import Session, select
        from models import User
        
        with Session(engine) as session:
            user = session.get(User, id)
            if not user:
                raise Exception("User not found")
            
            session.delete(user)
            session.commit()
            return True
    
    @strawberry.mutation
    def create_post(self, post_input: PostInput) -> PostType:
        from database import engine
        from sqlmodel import Session, select
        from models import Post, User
        
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
            
            # Get the post with author relationship
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
        
    @strawberry.mutation
    def update_post(self, id:int, title:Optional[str] = None, content:Optional[str] = None) -> Optional[PostType]:
        from database import engine
        from sqlmodel import Session, select
        from models import Post, User

        with Session(engine) as session:
            post = session.get(Post, id)
            if not post:
                raise Exception("Post not found")
            
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content

            session.add(post)
            session.commit()
            session.refresh(post)

            post_with_author = session.get(Post, post.id)

            return PostType(
                id=post_with_author.id,
                title=post_with_author.content,
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
        
    @strawberry.mutation
    def delete_post(self, id: int) -> bool:
        from database import engine
        from sqlmodel import Session, select
        from models import Post

        with Session(engine) as session:
            post = session.get(Post, id)
            if not post:
                raise Exception("Post not found")
            
            session.delete(post)
            session.commit()
            return True
        

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 10) -> int:
        for i in range(target):
            yield i
            await asyncio.sleep(1)

# Create schema
schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation, 
    subscription=Subscription
)

# Initialize database on startup
@asynccontextmanager
async def life_span(app: FastAPI):
    create_db_and_tables()
    print("Database tables created!")
    yield

    
# Create FastAPI app
app = FastAPI(
    title="GraphQL API with FastAPI",
    description="A modern GraphQL API built with FastAPI and Strawberry",
    version="1.0.0",
    lifespan=life_span
)

# Create GraphQL router
graphql_router = GraphQLRouter(schema)

# Add GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql")


# Health check and root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to GraphQL API",
        "graphql_playground": "/graphql",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GraphQL API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)