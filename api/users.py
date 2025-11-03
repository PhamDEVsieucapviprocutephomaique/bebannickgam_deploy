from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from models.models import Account, GameNick

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: str

class CreateUserRequest(BaseModel):
    username: str
    password: str

def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_session)):
    users = db.exec(select(Account).order_by(Account.created_at.desc())).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]

@router.post("/", response_model=UserResponse)
def create_user(user: CreateUserRequest, db: Session = Depends(get_session)):
    existing = db.exec(
        select(Account).where(Account.username == user.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    new_user = Account(
        username=user.username,
        password=user.password,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        created_at=new_user.created_at.isoformat()
    )

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    if user_id == 1:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản admin")
    
    user = db.get(Account, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    # TÌM VÀ XÓA TẤT CẢ NICK CỦA USER TRƯỚC
    user_nicks = db.exec(
        select(GameNick).where(GameNick.owner_id == user_id)
    ).all()
    
    # XÓA TẤT CẢ NICK CỦA USER
    for nick in user_nicks:
        db.delete(nick)
    
    # SAU ĐÓ XÓA USER
    db.delete(user)
    db.commit()
    
    return {
        "success": True, 
        "message": f"Đã xóa user và {len(user_nicks)} nick game của user này"
    }

@router.get("/{user_id}/nicks")
def get_user_nicks(user_id: int, db: Session = Depends(get_session)):
    nicks = db.exec(
        select(GameNick).where(GameNick.owner_id == user_id)
    ).all()
    
    return {
        "user_id": user_id,
        "nicks": [
            {
                "id": nick.id,
                "title": nick.title,
                "category": nick.category,
                "price": nick.price,
                "created_at": nick.created_at.isoformat()
            }
            for nick in nicks
        ]
    }