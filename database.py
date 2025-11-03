# database.py - Database configuration
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# SQLite database URL
DATABASE_URL = "sqlite:///./test.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)
print("------", engine, "------")
def create_db_and_tables():
    from models import User, Post
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    print("------------------------------------")

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session