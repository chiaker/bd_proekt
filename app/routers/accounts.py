from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Account, Transaction, TransactionBA, User
from app.schemas import AccountCreate, AccountResponse, AccountUpdate
from app.auth import require_permission
from decimal import Decimal

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(request: Request, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_permission(db, request, "accounts", "view")
    query = db.query(Account)
    if user_id:
        query = query.filter(Account.user_id == user_id)
    accounts = query.all()
    return accounts


@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "accounts", "create")
    if account.balance < 0:
        raise HTTPException(
            status_code=400, detail="Account balance cannot be negative")
    if not account.name:
        raise HTTPException(status_code=400, detail="Account name is required")
    user = db.query(User).filter(User.id == account.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_account = Account(
        user_id=account.user_id,
        name=account.name,
        type=account.type,
        balance=account.balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, payload: AccountUpdate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "accounts", "update")
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        account.user_id = payload.user_id
    if payload.name is not None:
        if not payload.name:
            raise HTTPException(
                status_code=400, detail="Account name is required")
        account.name = payload.name
    if payload.type is not None:
        account.type = payload.type
    if payload.balance is not None:
        if payload.balance < 0:
            raise HTTPException(
                status_code=400, detail="Account balance cannot be negative")
        account.balance = payload.balance
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "accounts", "delete")
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transfers = db.query(TransactionBA).filter(
        (TransactionBA.account_id_from == account_id) | (
            TransactionBA.account_id_to == account_id)
    ).all()
    for t in transfers:
        a_from = db.query(Account).filter(
            Account.id == t.account_id_from).with_for_update().first()
        a_to = db.query(Account).filter(
            Account.id == t.account_id_to).with_for_update().first()
        if a_from and a_to:
            amt = Decimal(str(t.amount))
            if account_id == t.account_id_from:
                if Decimal(a_to.balance) - amt < 0:
                    raise HTTPException(
                        status_code=400, detail="Cannot delete account: transfer rollback would cause negative balance")
                a_from.balance = Decimal(a_from.balance) + amt
                a_to.balance = Decimal(a_to.balance) - amt
            else:
                a_from.balance = Decimal(a_from.balance) + amt
                a_to.balance = Decimal(a_to.balance) - amt
        db.delete(t)

    db.query(Transaction).filter(Transaction.account_id ==
                                 account_id).delete(synchronize_session=False)

    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully"}
