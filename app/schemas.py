from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime


class AccountCreate(BaseModel):
    name: str
    type: str
    balance: float = 0.0


class AccountResponse(BaseModel):
    account_id: int
    user_id: int
    name: str
    type: str
    balance: float
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str
    type: str


class CategoryResponse(BaseModel):
    category_id: int
    user_id: int
    name: str
    type: str


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionResponse(BaseModel):
    transaction_id: int
    account_id: int
    category_id: int
    amount: float
    description: Optional[str]
    transaction_date: date
    created_at: datetime


class BudgetCreate(BaseModel):
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date


class BudgetResponse(BaseModel):
    budget_id: int
    user_id: int
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date
