from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
from app.database import get_db
from app.models import Transaction, Category

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/transactions")
async def get_transaction_report(start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db)):
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    transactions = query.all()
    return transactions


@router.get("/categories")
async def get_category_report(db: Session = Depends(get_db)):
    result = db.query(
        Category.name,
        Category.type,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).join(Transaction).group_by(Category.id, Category.name, Category.type).all()

    return [{"category": r.name, "type": r.type, "total_amount": float(r.total_amount), "count": r.transaction_count} for r in result]
