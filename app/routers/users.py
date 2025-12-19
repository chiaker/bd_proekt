from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Account, Transaction, TransactionBA, Category, Budget
from decimal import Decimal
from app.schemas import UserCreate, UserResponse, UserUpdate

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
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="User with same username or email already exists")
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.username and payload.username != user.username:
        exists = db.query(User).filter(
            User.username == payload.username, User.id != user_id).first()
        if exists:
            raise HTTPException(
                status_code=400, detail="Username already used")
        user.username = payload.username
    if payload.email and payload.email != user.email:
        exists = db.query(User).filter(
            User.email == payload.email, User.id != user_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already used")
        user.email = payload.email
    if payload.password:
        user.password_hash = payload.password
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    transfers = db.query(TransactionBA).filter(
        (TransactionBA.account_id_from.in_(account_ids)) | (
            TransactionBA.account_id_to.in_(account_ids))
    ).all()
    for t in transfers:
        a_from = db.query(Account).filter(
            Account.id == t.account_id_from).with_for_update().first()
        a_to = db.query(Account).filter(
            Account.id == t.account_id_to).with_for_update().first()
        if a_from and a_to:
            amt = Decimal(str(t.amount))
            if Decimal(a_to.balance) - amt < 0:
                raise HTTPException(
                    status_code=400, detail="Cannot delete user: transfer rollback would cause negative balance")
            a_from.balance = Decimal(a_from.balance) + amt
            a_to.balance = Decimal(a_to.balance) - amt
        db.delete(t)

    db.query(Transaction).filter(Transaction.account_id.in_(
        account_ids)).delete(synchronize_session=False)

    category_ids = [c.id for c in db.query(
        Category.id).filter(Category.user_id == user_id).all()]
    db.query(Budget).filter(Budget.category_id.in_(
        category_ids)).delete(synchronize_session=False)
    db.query(Category).filter(Category.id.in_(
        category_ids)).delete(synchronize_session=False)

    db.query(Account).filter(Account.id.in_(account_ids)
                             ).delete(synchronize_session=False)

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
