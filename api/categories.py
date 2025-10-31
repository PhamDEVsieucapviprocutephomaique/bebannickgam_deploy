from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from models.models import Category, GameNick

router = APIRouter()

# Pydantic schemas
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: str

    class Config:
        from_attributes = True

# Dependency
def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_session)):
    """
    Thêm category mới
    """
    # Check trùng
    existing = db.exec(
        select(Category).where(Category.name == category.name)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category đã tồn tại")
    
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        created_at=new_category.created_at.isoformat()
    )

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_session)):
    """
    Lấy tất cả categories
    """
    categories = db.exec(select(Category).order_by(Category.created_at)).all()
    
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            created_at=cat.created_at.isoformat()
        )
        for cat in categories
    ]

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_session)):
    """
    Xóa category (CHỈ XÓA ĐƯỢC NẾU KHÔNG CÒN NICK NÀO DÙNG CATEGORY ĐÓ)
    """
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category không tồn tại")
    
    # Check xem có nick nào đang dùng category này không
    nicks_using = db.exec(
        select(GameNick).where(GameNick.category == category.name)
    ).first()
    
    if nicks_using:
        raise HTTPException(
            status_code=400, 
            detail=f"Không thể xóa category '{category.name}' vì còn nick đang sử dụng"
        )
    
    db.delete(category)
    db.commit()
    
    return {"success": True, "message": "Xóa category thành công"}

@router.get("/names")
def get_category_names(db: Session = Depends(get_session)):
    """
    Lấy danh sách tên categories (để dùng cho dropdown)
    """
    categories = db.exec(select(Category)).all()
    return {"categories": [cat.name for cat in categories]}