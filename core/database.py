from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "DATABASE_URL=postgresql://neondb_owner:npg_jlXdUK9OBHV6@ep-steep-bird-ahyuk7fo-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Tạo tất cả tables trong database
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency để lấy database session
    """
    with Session(engine) as session:
        yield session 