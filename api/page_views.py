from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from models.models import PageView

router = APIRouter()

class PageViewResponse(BaseModel):
    count: int

def get_session():
    from core.database import engine
    with Session(engine) as session:
        yield session

@router.get("/", response_model=PageViewResponse)
def get_page_views(db: Session = Depends(get_session)):
    page_view = db.exec(select(PageView)).first()
    if not page_view:
        page_view = PageView(count=0)
        db.add(page_view)
        db.commit()
        db.refresh(page_view)
    
    return PageViewResponse(count=page_view.count)

@router.post("/increment")
def increment_page_views(db: Session = Depends(get_session)):
    page_view = db.exec(select(PageView)).first()
    if not page_view:
        page_view = PageView(count=1)
        db.add(page_view)
    else:
        page_view.count += 1
    
    db.commit()
    db.refresh(page_view)
    
    return PageViewResponse(count=page_view.count)