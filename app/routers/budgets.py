from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Budget
from app.schemas import BudgetCreate, BudgetResponse

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(db: Session = Depends(get_db)):
    budgets = db.query(Budget).all()
    return budgets


@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    db_budget = Budget(
        user_id=1,
        category_id=budget.category_id,
        amount_limit=budget.amount_limit,
        period_start=budget.period_start,
        period_end=budget.period_end
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget
