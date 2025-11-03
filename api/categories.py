from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from models.models import Category, GameNick

router = APIRouter()

# Pydantic schemas
class CategoryCreate(BaseModel):
    name: str

class CategoryReorder(BaseModel):
    category_id: int
    new_order: int

class CategoryResponse(BaseModel):
    id: int
    name: str
    order_index: int
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
    
    # Tìm order_index cao nhất và +1
    max_order = db.exec(select(Category.order_index).order_by(Category.order_index.desc())).first()
    new_order = (max_order or 0) + 1
    
    new_category = Category(name=category.name, order_index=new_order)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        order_index=new_category.order_index,
        created_at=new_category.created_at.isoformat()
    )

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_session)):
    """
    Lấy tất cả categories (đã sắp xếp theo order_index)
    """
    categories = db.exec(
        select(Category).order_by(Category.order_index.asc())
    ).all()
    
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            order_index=cat.order_index,
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
    categories = db.exec(
        select(Category).order_by(Category.order_index.asc())
    ).all()
    return {"categories": [cat.name for cat in categories]}

@router.put("/{category_id}/move-up")
def move_category_up(category_id: int, db: Session = Depends(get_session)):
    """
    Chuyển category lên trên
    """
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category không tồn tại")
    
    # Tìm category có order_index thấp hơn (ở trên)
    prev_category = db.exec(
        select(Category)
        .where(Category.order_index < category.order_index)
        .order_by(Category.order_index.desc())
    ).first()
    
    if prev_category:
        # Hoán đổi order_index
        temp_order = category.order_index
        category.order_index = prev_category.order_index
        prev_category.order_index = temp_order
        
        db.add(category)
        db.add(prev_category)
        db.commit()
        db.refresh(category)
        db.refresh(prev_category)
        
        return {
            "success": True, 
            "message": f"Đã chuyển '{category.name}' lên trên",
            "new_order": category.order_index
        }
    else:
        raise HTTPException(status_code=400, detail="Không thể chuyển lên trên nữa")

@router.put("/{category_id}/move-down")
def move_category_down(category_id: int, db: Session = Depends(get_session)):
    """
    Chuyển category xuống dưới
    """
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category không tồn tại")
    
    # Tìm category có order_index cao hơn (ở dưới)
    next_category = db.exec(
        select(Category)
        .where(Category.order_index > category.order_index)
        .order_by(Category.order_index.asc())
    ).first()
    
    if next_category:
        # Hoán đổi order_index
        temp_order = category.order_index
        category.order_index = next_category.order_index
        next_category.order_index = temp_order
        
        db.add(category)
        db.add(next_category)
        db.commit()
        db.refresh(category)
        db.refresh(next_category)
        
        return {
            "success": True, 
            "message": f"Đã chuyển '{category.name}' xuống dưới",
            "new_order": category.order_index
        }
    else:
        raise HTTPException(status_code=400, detail="Không thể chuyển xuống dưới nữa")

@router.put("/reorder")
def reorder_categories(reorder_list: List[CategoryReorder], db: Session = Depends(get_session)):
    """
    Sắp xếp lại toàn bộ categories (cho drag & drop trong tương lai)
    """
    for item in reorder_list:
        category = db.get(Category, item.category_id)
        if category:
            category.order_index = item.new_order
            db.add(category)
    
    db.commit()
    return {"success": True, "message": "Đã sắp xếp lại categories"}