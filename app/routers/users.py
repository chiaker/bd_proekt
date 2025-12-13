from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if not user.username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not user.email:
        raise HTTPException(status_code=400, detail="Email is required")
    # check uniqueness
    existing = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with same username or email already exists")
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
