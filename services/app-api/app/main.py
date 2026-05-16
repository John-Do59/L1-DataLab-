from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_db
from .schemas.schemas import UserCreate, UserResponse
from .repositories.user_repository import UserRepository

app = FastAPI(title="Ligue 1 Professional API", version="2.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Professional Ligue 1 API"}

@app.post("/users", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    
    # Vérification si l'email existe
    existing = await repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await repo.create(user_in)
    return new_user

@app.get("/health")
def health():
    return {"status": "healthy"}
