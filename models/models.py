from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str  # Lưu plain text như yêu cầu (không JWT, không hash)


class GameNick(SQLModel, table=True):
    __tablename__ = "game_nicks"
    
    id: int = Field(default=None, primary_key=True)
    title: str
    category: str
    price: float
    details: str  # Mô tả chi tiết
    facebook_link: str
    images: List[str] = Field(sa_column=Column(JSONB), default=[])  # Lưu array các image URLs
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)