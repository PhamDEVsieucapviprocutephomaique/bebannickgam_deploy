from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str
    role: str = Field(default="user")  # "admin" hoặc "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GameNick(SQLModel, table=True):
    __tablename__ = "game_nicks"
    
    id: int = Field(default=None, primary_key=True)
    title: str
    category: str
    price: float
    details: str
    facebook_link: str
    images: List[str] = Field(sa_column=Column(JSONB), default=[])
    owner_id: int = Field(default=1)  # Mặc định thuộc admin
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    order_index: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PageView(SQLModel, table=True):
    __tablename__ = "page_views"
    
    id: int = Field(default=None, primary_key=True)
    count: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)