from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class AccountCreate(BaseModel):
    name: str
    type: str
    balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str
    balance: float
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str
    type: str


class CategoryResponse(BaseModel):
    id: int
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
    id: int
    account_id: int
    category_id: int
    amount: float
    description: Optional[str]
    transaction_date: date


class TransactionBACreate(BaseModel):
    account_id_from: int
    account_id_to: int
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionBAResponse(BaseModel):
    id: int
    account_id_from: int
    account_id_to: int
    amount: float
    description: Optional[str]
    transaction_date: date


class BudgetCreate(BaseModel):
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date
