from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import create_db_and_tables, engine
from sqlmodel import Session, select
from models.models import Category, Account, PageView

# Import routers
from api.auth import router as auth_router
from api.game_nicks import router as game_nicks_router
from api.categories import router as categories_router
from api.users import router as users_router
from api.page_views import router as page_views_router

from api.upload import router as upload_router

from api.database import router as database_router

app = FastAPI(title="Game Nick Store API")





app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(game_nicks_router, prefix="/api/game-nicks", tags=["Game Nicks"])
app.include_router(categories_router, prefix="/api/categories", tags=["Categories"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(page_views_router, prefix="/api/page-views", tags=["Page Views"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(database_router, prefix="/api/database", tags=["database"])


@app.on_event("startup")
def on_startup():
    print("🚀 Creating database tables...")
    create_db_and_tables()
    
    # Thêm default categories
    with Session(engine) as db:
        existing_categories = db.exec(select(Category)).all()
        if not existing_categories:
            print("📝 Adding default categories...")
            default_categories = [
                "PUBG Mobile",
                "nick dưới 20 triệu", 
                "nick dưới 30 triệu",
                "nick vip trên 30 triệu"
            ]
            for index, cat_name in enumerate(default_categories):
                category = Category(name=cat_name, order_index=index)
                db.add(category)
            db.commit()
            print("✅ Default categories added")
        else:
            print(f"✅ Found {len(existing_categories)} existing categories")
        
        # Thêm admin account nếu chưa có
        admin_account = db.exec(select(Account).where(Account.id == 1)).first()
        if not admin_account:
            print("👑 Creating admin account...")
            admin = Account(
                id=1,
                username="admin",
                password="admin123",
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("✅ Admin account created")
        
        # Khởi tạo page views
        page_view = db.exec(select(PageView)).first()
        if not page_view:
            page_view = PageView(count=0)
            db.add(page_view)
            db.commit()
            print("✅ Page views initialized")

@app.get("/")
def root():
    return {"message": "Game Nick Store API", "version": "1.0.0", "docs": "/docs"}