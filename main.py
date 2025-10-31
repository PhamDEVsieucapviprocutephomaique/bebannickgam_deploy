from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import create_db_and_tables, engine
from sqlmodel import Session, select
from models.models import Category

# Import routers
from api.auth import router as auth_router
from api.game_nicks import router as game_nicks_router
from api.categories import router as categories_router

app = FastAPI(title="Game Nick Store API")

# CORS - Cho phép FE gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    game_nicks_router,
    prefix="/api/game-nicks",
    tags=["Game Nicks"]
)

app.include_router(
    categories_router,
    prefix="/api/categories",
    tags=["Categories"]
)

@app.on_event("startup")
def on_startup():
    """
    Khởi tạo database và thêm default categories
    """
    print("🚀 Creating database tables...")
    create_db_and_tables()
    
    # Thêm default categories nếu chưa có
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
            
            for cat_name in default_categories:
                category = Category(name=cat_name)
                db.add(category)
            
            db.commit()
            print("✅ Default categories added")
        else:
            print(f"✅ Found {len(existing_categories)} existing categories")

@app.get("/")
def root():
    return {
        "message": "Game Nick Store API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}