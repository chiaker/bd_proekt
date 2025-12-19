from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Category, Transaction, Budget, User
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.auth import require_permission

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(request: Request, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_permission(db, request, "categories", "view")
    query = db.query(Category)
    if user_id:
        query = query.filter(Category.user_id == user_id)
    categories = query.all()
    return categories


@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "categories", "create")
    if not category.name:
        raise HTTPException(
            status_code=400, detail="Category name is required")
    if category.type not in ('income', 'expense'):
        raise HTTPException(
            status_code=400, detail="Category type must be 'income' or 'expense'")
    user = db.query(User).filter(User.id == category.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_category = Category(
        user_id=category.user_id,
        name=category.name,
        type=category.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, payload: CategoryUpdate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "categories", "update")
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        category.user_id = payload.user_id
    if payload.name is not None:
        if not payload.name:
            raise HTTPException(
                status_code=400, detail="Category name is required")
        category.name = payload.name
    if payload.type is not None:
        if payload.type not in ('income', 'expense'):
            raise HTTPException(
                status_code=400, detail="Category type must be 'income' or 'expense'")
        category.type = payload.type
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "categories", "delete")
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.query(Transaction).filter(Transaction.category_id ==
                                 category_id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.category_id ==
                            category_id).delete(synchronize_session=False)
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
