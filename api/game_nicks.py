from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from models.models import GameNick

router = APIRouter()

class GameNickCreate(BaseModel):
    title: str
    category: str
    price: float
    details: str
    facebook_link: str = "https://www.facebook.com/letuan089"
    images: List[str] = []
    owner_id: int = 1  # Mặc định

class GameNickResponse(BaseModel):
    id: int
    title: str
    category: str
    price: float
    details: str
    facebook_link: str
    images: List[str]
    owner_id: int
    created_at: str

def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.post("/", response_model=GameNickResponse)
def create_game_nick(nick: GameNickCreate, db: Session = Depends(get_session)):
    new_nick = GameNick(
        title=nick.title,
        category=nick.category,
        price=nick.price,
        details=nick.details,
        facebook_link=nick.facebook_link,
        images=nick.images,
        owner_id=nick.owner_id
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
        owner_id=new_nick.owner_id,
        created_at=new_nick.created_at.isoformat()
    )

@router.get("/", response_model=List[GameNickResponse])
def get_all_game_nicks(db: Session = Depends(get_session)):
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
            owner_id=nick.owner_id,
            created_at=nick.created_at.isoformat()
        )
        for nick in nicks
    ]

@router.delete("/{nick_id}")
def delete_game_nick(nick_id: int, current_user_id: int = 1, db: Session = Depends(get_session)):
    nick = db.get(GameNick, nick_id)
    if not nick:
        raise HTTPException(status_code=404, detail="Nick không tồn tại")
    
    # Check permission: chỉ owner hoặc admin (user_id=1) được xóa
    if nick.owner_id != current_user_id and current_user_id != 1:
        raise HTTPException(status_code=403, detail="Không có quyền xóa nick này")
    
    db.delete(nick)
    db.commit()
    
    return {"success": True, "message": "Xóa thành công"}