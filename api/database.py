from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, delete
from pydantic import BaseModel
from typing import List, Dict, Any
from models.models import Account, GameNick, Category, PageView

router = APIRouter()

class BulkDeleteRequest(BaseModel):
    table_name: str
    ids: List[int]

def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.get("/tables")
def get_all_tables_data(db: Session = Depends(get_session)):
    """Lấy dữ liệu từ tất cả các bảng"""
    tables_data = {}
    
    # Lấy dữ liệu accounts
    accounts = db.exec(select(Account)).all()
    tables_data["accounts"] = [
        {
            "id": acc.id,
            "username": acc.username,
            "role": acc.role,
            "created_at": acc.created_at.isoformat()
        }
        for acc in accounts
    ]
    
    # Lấy dữ liệu game_nicks
    game_nicks = db.exec(select(GameNick)).all()
    tables_data["game_nicks"] = [
        {
            "id": nick.id,
            "title": nick.title,
            "category": nick.category,
            "price": nick.price,
            "details": nick.details,
            "facebook_link": nick.facebook_link,
            "images": nick.images,
            "owner_id": nick.owner_id,
            "created_at": nick.created_at.isoformat()
        }
        for nick in game_nicks
    ]
    
    # Lấy dữ liệu categories
    categories = db.exec(select(Category)).all()
    tables_data["categories"] = [
        {
            "id": cat.id,
            "name": cat.name,
            "order_index": cat.order_index,
            "created_at": cat.created_at.isoformat()
        }
        for cat in categories
    ]
    
    # Lấy dữ liệu page_views
    page_views = db.exec(select(PageView)).all()
    tables_data["page_views"] = [
        {
            "id": pv.id,
            "count": pv.count,
            "last_updated": pv.last_updated.isoformat() if pv.last_updated else None
        }
        for pv in page_views
    ]
    
    return tables_data

@router.post("/bulk-delete")
def bulk_delete_records(request: BulkDeleteRequest, db: Session = Depends(get_session)):
    """Xóa hàng loạt bản ghi từ các bảng"""
    
    if request.table_name == "accounts":
        # Không cho xóa admin (id=1)
        ids_to_delete = [id for id in request.ids if id != 1]
        if len(ids_to_delete) != len(request.ids):
            raise HTTPException(status_code=400, detail="Không thể xóa tài khoản admin")
        
        for record_id in ids_to_delete:
            record = db.get(Account, record_id)
            if record:
                db.delete(record)
    
    elif request.table_name == "game_nicks":
        for record_id in request.ids:
            record = db.get(GameNick, record_id)
            if record:
                db.delete(record)
    
    elif request.table_name == "categories":
        for record_id in request.ids:
            record = db.get(Category, record_id)
            if record:
                db.delete(record)
    
    elif request.table_name == "page_views":
        for record_id in request.ids:
            record = db.get(PageView, record_id)
            if record:
                db.delete(record)
    
    else:
        raise HTTPException(status_code=400, detail="Tên bảng không hợp lệ")
    
    db.commit()
    
    return {
        "success": True, 
        "message": f"Đã xóa {len(request.ids)} bản ghi từ bảng {request.table_name}"
    }

@router.delete("/clear-table/{table_name}")
def clear_entire_table(table_name: str, db: Session = Depends(get_session)):
    """Xóa toàn bộ dữ liệu trong bảng (trừ admin account)"""
    
    if table_name == "accounts":
        # Xóa tất cả accounts trừ admin (id=1)
        db.exec(delete(Account).where(Account.id != 1))
        message = "Đã xóa tất cả tài khoản (trừ admin)"
    
    elif table_name == "game_nicks":
        db.exec(delete(GameNick))
        message = "Đã xóa tất cả nick game"
    
    elif table_name == "categories":
        db.exec(delete(Category))
        message = "Đã xóa tất cả categories"
    
    elif table_name == "page_views":
        db.exec(delete(PageView))
        message = "Đã xóa tất cả page views"
    
    else:
        raise HTTPException(status_code=400, detail="Tên bảng không hợp lệ")
    
    db.commit()
    
    return {"success": True, "message": message}