from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from models.models import Account

router = APIRouter()

# Pydantic schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: str | None = None

# Dependency
def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_session)):
    """
    Đăng nhập đơn giản - check username/password
    """
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
        username=account.username
    )

@router.post("/register")
def register(request: LoginRequest, db: Session = Depends(get_session)):
    """
    Đăng ký tài khoản mới
    """
    # Check username đã tồn tại chưa
    existing = db.exec(
        select(Account).where(Account.username == request.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    # Tạo account mới
    new_account = Account(
        username=request.username,
        password=request.password
    )
    db.add(new_account)
    db.commit()
    
    return {"success": True, "message": "Đăng ký thành công"}