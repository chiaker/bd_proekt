from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Account
from app.schemas import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts


@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = Account(
        user_id=1,
        name=account.name,
        type=account.type,
        balance=account.balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account
