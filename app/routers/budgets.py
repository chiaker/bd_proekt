from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Budget, Category, User
from app.schemas import BudgetCreate, BudgetResponse, BudgetUpdate
from app.auth import require_permission

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(request: Request, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_permission(db, request, "budgets", "view")
    query = db.query(Budget)
    if user_id:
        query = query.filter(Budget.user_id == user_id)
    budgets = query.all()
    return budgets


@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "budgets", "create")
    # basic validation
    if budget.amount_limit <= 0:
        raise HTTPException(
            status_code=400, detail="Budget amount_limit must be greater than zero")
    if budget.period_start > budget.period_end:
        raise HTTPException(
            status_code=400, detail="Budget period_start must be before period_end")
    user = db.query(User).filter(User.id == budget.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cat = db.query(Category).filter(Category.id == budget.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.user_id != budget.user_id:
        raise HTTPException(
            status_code=400, detail="Category belongs to another user")
    db_budget = Budget(
        user_id=budget.user_id,
        category_id=budget.category_id,
        amount_limit=budget.amount_limit,
        period_start=budget.period_start,
        period_end=budget.period_end
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: int, payload: BudgetUpdate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "budgets", "update")
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        budget.user_id = payload.user_id
    if payload.category_id:
        cat = db.query(Category).filter(
            Category.id == payload.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        if budget.user_id and cat.user_id != budget.user_id:
            raise HTTPException(
                status_code=400, detail="Category belongs to another user")
        budget.category_id = payload.category_id
    if payload.amount_limit is not None:
        if payload.amount_limit <= 0:
            raise HTTPException(
                status_code=400, detail="Budget amount_limit must be greater than zero")
        budget.amount_limit = payload.amount_limit
    if payload.period_start:
        budget.period_start = payload.period_start
    if payload.period_end:
        budget.period_end = payload.period_end
    if budget.period_start > budget.period_end:
        raise HTTPException(
            status_code=400, detail="Budget period_start must be before period_end")
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "budgets", "delete")
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}
