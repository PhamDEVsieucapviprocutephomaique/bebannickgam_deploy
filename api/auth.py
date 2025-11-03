from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from models.models import Account

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: str | None = None
    role: str | None = None
    user_id: int | None = None

class RegisterRequest(BaseModel):
    username: str
    password: str

def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_session)):
    account = db.exec(
        select(Account).where(
            Account.username == request.username,
            Account.password == request.password
        )
    ).first()
    
    if not account:
        raise HTTPException(status_code=401, detail="Username hoặc password không đúng")
    
    return LoginResponse(
        success=True,
        message="Đăng nhập thành công",
        username=account.username,
        role=account.role,
        user_id=account.id
    )

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_session)):
    existing = db.exec(
        select(Account).where(Account.username == request.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    new_account = Account(
        username=request.username,
        password=request.password,
        role="user"
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return {
        "success": True, 
        "message": "Đăng ký thành công",
        "user_id": new_account.id
    }