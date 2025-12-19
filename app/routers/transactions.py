from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from sqlalchemy import func
from app.models import Transaction, TransactionBA, Account, Category, Budget
from app.auth import require_permission
from decimal import Decimal
from app.schemas import TransactionCreate, TransactionResponse, TransactionBACreate, TransactionBAResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(request: Request, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "view")
    query = db.query(Transaction)
    if user_id:
        query = query.join(Account).filter(Account.user_id == user_id)
    transactions = query.all()
    return transactions


@router.get("/ba", response_model=List[TransactionBAResponse])
async def get_transfers(request: Request, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "view")
    query = db.query(TransactionBA)
    if user_id:
        account_ids = [row.id for row in db.query(
            Account.id).filter(Account.user_id == user_id).all()]
        if account_ids:
            query = query.filter((TransactionBA.account_id_from.in_(account_ids)) | (
                TransactionBA.account_id_to.in_(account_ids)))
        else:
            return []
    transfers = query.all()
    return transfers


@router.get("/ba/{transfer_id}", response_model=TransactionBAResponse)
async def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    db_transfer = db.query(TransactionBA).filter(
        TransactionBA.id == transfer_id).first()
    if not db_transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return db_transfer


@router.post("/ba", response_model=TransactionBAResponse)
async def create_transfer(transfer: TransactionBACreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "create")
    # Basic validation: accounts must be different and amount positive
    if transfer.account_id_from == transfer.account_id_to:
        raise HTTPException(
            status_code=400, detail="Source and destination accounts must be different")
    if transfer.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transfer amount must be greater than zero")

    # Ensure accounts exist
    a_from = db.query(Account).filter(
        Account.id == transfer.account_id_from).with_for_update().first()
    a_to = db.query(Account).filter(
        Account.id == transfer.account_id_to).with_for_update().first()
    if not a_from or not a_to:
        raise HTTPException(status_code=404, detail="Account not found")
    if a_from.user_id != a_to.user_id:
        raise HTTPException(
            status_code=400, detail="Accounts belong to different users")
    db_transfer = TransactionBA(
        account_id_from=transfer.account_id_from,
        account_id_to=transfer.account_id_to,
        amount=transfer.amount,
        description=transfer.description,
        transaction_date=transfer.transaction_date or date.today()
    )
    # apply balance change
    # convert to Decimal for safety
    delta = Decimal(str(transfer.amount))
    # optional: prevent overdraft
    if Decimal(a_from.balance) - delta < 0:
        raise HTTPException(
            status_code=400, detail="Insufficient funds in source account")
    a_from.balance = Decimal(a_from.balance) - delta
    a_to.balance = Decimal(a_to.balance) + delta
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer


@router.put("/ba/{transfer_id}", response_model=TransactionBAResponse)
async def update_transfer(transfer_id: int, transfer: TransactionBACreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "update")
    db_transfer = db.query(TransactionBA).filter(
        TransactionBA.id == transfer_id).first()
    if not db_transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if transfer.account_id_from == transfer.account_id_to:
        raise HTTPException(
            status_code=400, detail="Source and destination accounts must be different")
    if transfer.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transfer amount must be greater than zero")

    # lock accounts
    a_old_from = db.query(Account).filter(
        Account.id == db_transfer.account_id_from).with_for_update().first()
    a_old_to = db.query(Account).filter(
        Account.id == db_transfer.account_id_to).with_for_update().first()
    a_new_from = db.query(Account).filter(
        Account.id == transfer.account_id_from).with_for_update().first()
    a_new_to = db.query(Account).filter(
        Account.id == transfer.account_id_to).with_for_update().first()
    if not a_new_from or not a_new_to:
        raise HTTPException(status_code=404, detail="Account not found")
    if not a_old_from or not a_old_to:
        raise HTTPException(status_code=404, detail="Account not found")
    if a_new_from.user_id != a_new_to.user_id:
        raise HTTPException(
            status_code=400, detail="Accounts belong to different users")

    old_amount = Decimal(str(db_transfer.amount))
    new_amount = Decimal(str(transfer.amount))

    # compute hypothetical final balances to ensure no overdrafts
    # start from current balances
    b_old_from = Decimal(a_old_from.balance)
    b_old_to = Decimal(a_old_to.balance)
    b_new_from = Decimal(a_new_from.balance)
    b_new_to = Decimal(a_new_to.balance)

    # compute final balances after reversal and new apply
    # reverse old
    b_old_from_after = b_old_from + old_amount
    b_old_to_after = b_old_to - old_amount
    # apply new
    if a_new_from.id == a_old_from.id:
        b_from_final = b_old_from_after - new_amount
    else:
        b_from_final = b_new_from - new_amount

    if a_new_to.id == a_old_to.id:
        b_to_final = b_old_to_after + new_amount
    else:
        b_to_final = b_new_to + new_amount

    if b_from_final < 0:
        raise HTTPException(
            status_code=400, detail="Insufficient funds in source account after update")

    # apply reversal and new amounts to actual account objects
    a_old_from.balance = b_old_from_after
    a_old_to.balance = b_old_to_after
    a_new_from.balance = Decimal(a_new_from.balance) - new_amount
    a_new_to.balance = Decimal(a_new_to.balance) + new_amount

    db_transfer.account_id_from = transfer.account_id_from
    db_transfer.account_id_to = transfer.account_id_to
    db_transfer.amount = transfer.amount
    db_transfer.description = transfer.description
    db_transfer.transaction_date = transfer.transaction_date or date.today()

    db.commit()
    db.refresh(db_transfer)
    return db_transfer


@router.delete("/ba/{transfer_id}")
async def delete_transfer(transfer_id: int, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "delete")
    db_transfer = db.query(TransactionBA).filter(
        TransactionBA.id == transfer_id).first()
    if not db_transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    # reverse balances
    a_from = db.query(Account).filter(
        Account.id == db_transfer.account_id_from).with_for_update().first()
    a_to = db.query(Account).filter(
        Account.id == db_transfer.account_id_to).with_for_update().first()
    if a_from and a_to:
        amt = Decimal(str(db_transfer.amount))
        if Decimal(a_to.balance) - amt < 0:
            raise HTTPException(
                status_code=400, detail="Cannot delete transfer: would cause negative balance on destination account")
        a_from.balance = Decimal(a_from.balance) + amt
        a_to.balance = Decimal(a_to.balance) - amt

    db.delete(db_transfer)
    db.commit()
    return {"message": "Transfer deleted successfully"}


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


@router.post("/", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "create")
    # validation
    if transaction.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transaction amount must be greater than zero")
    # fetch account and category, lock account for update
    acc = db.query(Account).filter(
        Account.id == transaction.account_id).with_for_update().first()
    cat = db.query(Category).filter(
        Category.id == transaction.category_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if acc.user_id != cat.user_id:
        raise HTTPException(
            status_code=400, detail="Account and category belong to different users")

    # compute delta
    amt = Decimal(str(transaction.amount))
    trans_date = transaction.transaction_date or date.today()
    # Budget checks: if this is an expense category, ensure budget limits are not exceeded
    if cat.type == 'expense':
        budgets = db.query(Budget).filter(
            Budget.category_id == transaction.category_id,
            Budget.period_start <= trans_date,
            Budget.period_end >= trans_date,
        ).all()
        for b in budgets:
            # sum existing spending in this budget period for the category
            spent = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.category_id == transaction.category_id,
                Transaction.transaction_date >= b.period_start,
                Transaction.transaction_date <= b.period_end,
            ).scalar() or 0
            new_spent = Decimal(str(spent)) + amt
            if new_spent > Decimal(str(b.amount_limit)):
                raise HTTPException(
                    status_code=400, detail=f"Budget exceeded for category during period {b.period_start} - {b.period_end}")
    delta = amt if cat.type == 'income' else -amt
    # optional check: ensure expense doesn't create negative balance
    if cat.type == 'expense' and Decimal(acc.balance) + delta < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    # apply balance change
    acc.balance = Decimal(acc.balance) + delta

    db_transaction = Transaction(
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=trans_date
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, transaction: TransactionCreate, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "update")
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # fetch involved accounts and categories with locks
    old_acc = db.query(Account).filter(
        Account.id == db_transaction.account_id).with_for_update().first()
    old_cat = db.query(Category).filter(
        Category.id == db_transaction.category_id).first()
    new_acc = db.query(Account).filter(
        Account.id == transaction.account_id).with_for_update().first()
    new_cat = db.query(Category).filter(
        Category.id == transaction.category_id).first()
    if not new_acc or not new_cat:
        raise HTTPException(
            status_code=404, detail="Account or category not found")
    if new_acc.user_id != new_cat.user_id:
        raise HTTPException(
            status_code=400, detail="Account and category belong to different users")

    old_amt = Decimal(str(db_transaction.amount))
    new_amt = Decimal(str(transaction.amount))
    old_delta = old_amt if old_cat.type == 'income' else -old_amt
    new_delta = new_amt if new_cat.type == 'income' else -new_amt

    new_trans_date = transaction.transaction_date or date.today()
    # Budget checks for new category/date if it's an expense
    if new_cat.type == 'expense':
        budgets = db.query(Budget).filter(
            Budget.category_id == transaction.category_id,
            Budget.period_start <= new_trans_date,
            Budget.period_end >= new_trans_date,
        ).all()
        for b in budgets:
            # sum existing spending in this budget period for the category excluding this transaction
            spent = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.category_id == transaction.category_id,
                Transaction.transaction_date >= b.period_start,
                Transaction.transaction_date <= b.period_end,
                Transaction.id != db_transaction.id,
            ).scalar() or 0
            new_spent = Decimal(str(spent)) + new_amt
            if new_spent > Decimal(str(b.amount_limit)):
                raise HTTPException(
                    status_code=400, detail=f"Budget exceeded for category during period {b.period_start} - {b.period_end}")

    # reverse old effect
    # compute hypothetical new balances for safety checks
    if old_acc.id == new_acc.id:
        hypothetical = Decimal(old_acc.balance) - old_delta + new_delta
        if hypothetical < 0:
            raise HTTPException(status_code=400, detail="Insufficient funds")
    else:
        if Decimal(old_acc.balance) - old_delta < 0:
            raise HTTPException(
                status_code=400, detail="Insufficient funds on old account for reversal")
        if Decimal(new_acc.balance) + new_delta < 0:
            raise HTTPException(
                status_code=400, detail="Insufficient funds on new account")

    old_acc.balance = Decimal(old_acc.balance) - old_delta
    # apply new effect
    new_acc.balance = Decimal(new_acc.balance) + new_delta

    db_transaction.account_id = transaction.account_id
    db_transaction.category_id = transaction.category_id
    db_transaction.amount = transaction.amount
    db_transaction.description = transaction.description
    db_transaction.transaction_date = new_trans_date

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, request: Request, db: Session = Depends(get_db)):
    require_permission(db, request, "transactions", "delete")
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # reverse the transaction's effect on the account
    acc = db.query(Account).filter(
        Account.id == db_transaction.account_id).with_for_update().first()
    cat = db.query(Category).filter(
        Category.id == db_transaction.category_id).first()
    if acc and cat:
        amt = Decimal(str(db_transaction.amount))
        delta = amt if cat.type == 'income' else -amt
        # ensure deletion won't make balance negative
        if Decimal(acc.balance) - delta < 0:
            raise HTTPException(
                status_code=400, detail="Cannot delete transaction: would cause negative balance on account")
        # reverse effect -> subtract delta
        acc.balance = Decimal(acc.balance) - delta
    db.delete(db_transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}
