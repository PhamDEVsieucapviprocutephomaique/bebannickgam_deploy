from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from models.models import GameNick

router = APIRouter()

# Pydantic schemas
class GameNickCreate(BaseModel):
    title: str
    category: str
    price: float
    details: str
    facebook_link: str = "https://www.facebook.com/letuan089"
    images: List[str] = []

class GameNickResponse(BaseModel):
    id: int
    title: str
    category: str
    price: float
    details: str
    facebook_link: str
    images: List[str]
    created_at: str

    class Config:
        from_attributes = True

# Dependency
def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.post("/", response_model=GameNickResponse)
def create_game_nick(nick: GameNickCreate, db: Session = Depends(get_session)):
    """
    Thêm nick game mới
    """
    new_nick = GameNick(
        title=nick.title,
        category=nick.category,
        price=nick.price,
        details=nick.details,
        facebook_link=nick.facebook_link,
        images=nick.images
    )
    db.add(new_nick)
    db.commit()
    db.refresh(new_nick)
    
    return GameNickResponse(
        id=new_nick.id,
        title=new_nick.title,
        category=new_nick.category,
        price=new_nick.price,
        details=new_nick.details,
        facebook_link=new_nick.facebook_link,
        images=new_nick.images,
        created_at=new_nick.created_at.isoformat()
    )

@router.get("/", response_model=List[GameNickResponse])
def get_all_game_nicks(db: Session = Depends(get_session)):
    """
    Lấy tất cả game nicks
    """
    nicks = db.exec(select(GameNick).order_by(GameNick.created_at.desc())).all()
    
    return [
        GameNickResponse(
            id=nick.id,
            title=nick.title,
            category=nick.category,
            price=nick.price,
            details=nick.details,
            facebook_link=nick.facebook_link,
            images=nick.images,
            created_at=nick.created_at.isoformat()
        )
        for nick in nicks
    ]

@router.get("/{nick_id}", response_model=GameNickResponse)
def get_game_nick(nick_id: int, db: Session = Depends(get_session)):
    """
    Lấy chi tiết 1 nick
    """
    nick = db.get(GameNick, nick_id)
    if not nick:
        raise HTTPException(status_code=404, detail="Nick không tồn tại")
    
    return GameNickResponse(
        id=nick.id,
        title=nick.title,
        category=nick.category,
        price=nick.price,
        details=nick.details,
        facebook_link=nick.facebook_link,
        images=nick.images,
        created_at=nick.created_at.isoformat()
    )

@router.delete("/{nick_id}")
def delete_game_nick(nick_id: int, db: Session = Depends(get_session)):
    """
    Xóa nick game
    """
    nick = db.get(GameNick, nick_id)
    if not nick:
        raise HTTPException(status_code=404, detail="Nick không tồn tại")
    
    db.delete(nick)
    db.commit()
    
    return {"success": True, "message": "Xóa thành công"}

@router.get("/category/{category_name}", response_model=List[GameNickResponse])
def get_nicks_by_category(category_name: str, db: Session = Depends(get_session)):
    """
    Lấy nicks theo category
    """
    nicks = db.exec(
        select(GameNick)
        .where(GameNick.category == category_name)
        .order_by(GameNick.created_at.desc())
    ).all()
    
    return [
        GameNickResponse(
            id=nick.id,
            title=nick.title,
            category=nick.category,
            price=nick.price,
            details=nick.details,
            facebook_link=nick.facebook_link,
            images=nick.images,
            created_at=nick.created_at.isoformat()
        )
        for nick in nicks
    ]